import _ from 'lodash'
import constants from '@/store/whiteboarding/utils/constants'
import FABRIC_MULTIPLE_SELECT_TYPE from '@/store/whiteboarding/utils/constants'
import socket from './socket'
import store from '@/store'
import utils from '@/api/api-utils'
import Vue from 'vue'
import {fabric} from 'fabric'

const p = Vue.prototype

/**
 * Add an asset to the whiteboard canvas
 * asset: The asset that should be added to the whiteboard canvas
 */
const addAsset = (asset: any, state: any) => {
  // Switch the toolbar back to move mode
  store.commit('whiteboarding/setMode', 'move')

  // Default to a placeholder when the asset does not have a preview image
  if (!asset.imageUrl) {
    if (asset.type === 'file' && asset.mime.indexOf('image/') !== -1) {
      asset.imageUrl = asset.downloadUrl
    } else {
      asset.imageUrl = constants.ASSET_PLACEHOLDERS[asset.type]
    }
  }

  if (_.startsWith(asset.imageUrl, 's3://')) {
    // Assets stored in S3 must be pulled from SuiteC route
    asset.imageUrl = `${utils.apiBaseUrl()}/assets/${asset.id}/download`
  }

  // Add the asset to the center of the whiteboard canvas
  const connector = _.includes(asset.imageUrl, '?') ? '&' : '?'
  const imageUrl = asset.imageUrl + connector + 'track=false'
  fabric.Image.fromURL(imageUrl, (element: any) => {
    // This will exclude the toolbar and sidebar, if expanded.
    // Calculate the center point of the whiteboard canvas.
    const zoomLevel = p.$canvas.getZoom()
    const canvasCenter = {
      x: ((state.viewport.clientWidth / 2) + state.viewport.scrollLeft) / zoomLevel,
      y: ((state.viewport.clientHeight / 2) + state.viewport.scrollTop) / zoomLevel
    }

    // Scale the element to ensure it takes up a maximum of 80% of the
    // visible viewport width and height
    const maxWidth = state.viewport.clientWidth * 0.8 / p.$canvas.getZoom()
    const widthRatio = maxWidth / element.width
    const maxHeight = state.viewport.clientHeight * 0.8 / p.$canvas.getZoom()
    const heightRatio = maxHeight / element.height
    // Determine which side needs the most scaling for the element to fit on the screen
    const ratio = _.min([widthRatio, heightRatio])
    if (ratio < 1) {
      element.scale(ratio)
    }

    element.left = canvasCenter.x
    element.top = canvasCenter.y

    // Add the asset id to the element
    element.assetId = asset.id

    // Add the new element to the canvas
    p.$canvas.add(element)
    p.$canvas.setActiveObject(element)
  })
}

/**
 * Calculate the position of an element in a group relative to the whiteboard canvas
 *
 * @param  {Object}         selection         The selection (group of objects) of which the element is a part
 * @param  {Object}         element           The Fabric.js element for which the position relative to its group should be calculated
 * @return {Object}                           The position of the element relative to the whiteboard canvas. Will return the `angle`, `left` and `top` postion and the `scaleX` and `scaleY` scaling factors
 */
const calculateGlobalElementPosition = (selection: any, element: any): any => {
  const center = selection.getCenterPoint()
  const rotated = $_calculateRotatedLeftTop(selection, element)
  return {
    angle: element.getAngle() + selection.getAngle(),
    left: center.x + rotated.left,
    scaleX: element.get('scaleX') * selection.get('scaleX'),
    scaleY: element.get('scaleY') * selection.get('scaleY'),
    top: center.y + rotated.top
  }
}

/**
 * Delete the selected whiteboard element(s)
 */
const deleteActiveElements = (state: any) => {
  // Get the selected items
  const elements = getActiveElements()
  // Delete the selected items
  _.each(elements, (element: any) => p.$canvas.remove(getCanvasElement(element.uuid)))
  // If a group selection was made, remove the group as well in case Fabric doesn't clean up after itself
  const selection = p.$canvas.getActiveObject()
  if (selection.type === FABRIC_MULTIPLE_SELECT_TYPE) {
    p.$canvas.remove(selection)
    p.$canvas.discardActiveObject().requestRenderAll()
  }
  $_saveDeleteElements(elements, state)
}

const deserializeElement = (state: any, element: any, callback: any) => {
  // Convert a serialized Fabric.js canvas element to a proper Fabric.js canvas element
  // element: The serialized Fabric.js canvas element to deserialize
  // callback: Standard callback function
  element = _.cloneDeep(element)
  // Make the element unseletable when the whiteboard is rendered in read only mode
  if (state.whiteboard.deletedAt) {
    element.selectable = false
  }
  // Extract the type from the serialized element
  const type = fabric.util.string.camelize(fabric.util.string.capitalize(element.type))
  if (element.type === 'image') {
    // In order to avoid cross-domain errors when loading images from different domains,
    // the source of the element needs to be temporarily cleared and set manually once
    // the element has been created
    element.realSrc = element.src
    element.src = ''
    callback = (e: any) => {
      e.setSrc(e.get('realSrc'), () => callback(e))
    }
  // TODO: Why the special treatment for 'async'?
  // } else if (fabric[type].async) {
  //   fabric[type].fromObject(element, callback)
  // } else {
  //   fabric[type].fromObject(element)
  }
  return fabric[type].fromObject(element, callback)
}

/**
 * Enable or disable all elements on the whiteboard canvas. When an element is disabled, it will not be possible
 * to select, move or modify it
 *
 * enabled: Whether the elements on the whiteboard canvas should be enabled or disabled
 */
const enableCanvasElements = (enabled: boolean) => {
  p.$canvas.selection = enabled
  _.each(p.$canvas.getObjects(), (element: any) => element.selectable = enabled)
}

/**
 * Ensure that the currently active object or group can not be positioned off screen
 *
 * event: The event representing the active object or group
 */
const ensureWithinCanvas = (event: any) => {
  const element = event.target
  // Don't allow the element's or group's bounding rectangle
  // to go off screen
  element.setCoords()
  const bound = element.getBoundingRect()
  if (bound.left < 0) {
    element.left -= bound.left / p.$canvas.getZoom()
  }
  if (bound.top < 0) {
    element.top -= bound.top / p.$canvas.getZoom()
  }
}

const init = (state: any) => {
  /**
   * Extend the Fabric.js `toObject` deserialization function to include
   * the property that uniquely identifies an object on the canvas, as well as
   * a property containing the index of the object relative to the other items
   * on the canvas
   */
   fabric.Object.prototype.toObject = (function(toObject) {
    return function() {
      const object:any = this
      return fabric.util.object.extend(toObject.call(object), {
        assetId: object.assetId,
        height: object.height,
        index: p.$canvas.getObjects().indexOf(object),
        uuid: object.uuid,
        width: object.width
      })
    }
  }(fabric.Object.prototype.toObject))

  /**
   * An IText whiteboard canvas element was updated by the current user
   */
  fabric.IText.prototype.on('editing:exited', function() {
    const element:any = this
    if (element) {
      // If the text element is empty, it can be removed from the whiteboard canvas
      const text = element.text.trim()
      if (!text) {
        if (element.get('uuid')) {
          $_saveDeleteElements(state, [element])
        }
        p.$canvas.remove(element)
      } else if (!element.get('uuid')) {
        // The text element did not exist before. Notify the server that the element was added
        saveNewElement(element, state)
      } else {
        // The text element existed before. Notify the server that the element was updated
        saveElementUpdates([element], state)
      }
      store.commit('whiteboarding/setMode', 'move')
    }
  })
  // Recalculate the size of the p.$canvas when the window is resized
  window.addEventListener('resize', () => setCanvasDimensions(state))
}

const getActiveElements = (): any[] => {
  // Get the currently selected whiteboard elements
  // return the selected whiteboard elements
  const activeElements: any[] = []
  const selection = p.$canvas.getActiveObject()
  if (selection.type === FABRIC_MULTIPLE_SELECT_TYPE) {
    _.each(selection.objects, (element: any) => {
      // When a Fabric.js canvas element is part of a group selection, its properties will be
      // relative to the group. Therefore, we calculate the actual position of each element in
      // the group relative to the whiteboard canvas
      const position = calculateGlobalElementPosition(selection, element)
      activeElements.push(_.assignTo({}, element.toObject(), position))
    })
  } else if (p.$canvas.getActiveObject()) {
    activeElements.push(p.$canvas.getActiveObject().toObject())
  }
  return activeElements
}

const getCanvasElement = (uuid: number) => {
  _.each(p.$canvas.getObjects(), (element: any) => {
    if (element.get('uuid') === uuid) {
      return element
    }
  })
  return null
}

/**
 * Paste the copied element(s)
 */
const paste = (state: any): void => {
  const elements: any[] = []

  // Activate the pasted element(s)
  const selectPasted = _.after(state.clipboard.length, function() {
    // When only a single element was pasted, simply select it
    if (elements.length === 1) {
      p.$canvas.setActiveObject(elements[0])
    // When multiple elements were pasted, create a new group
    // for those elements and select them
    } else {
      const selection = new fabric.ActiveSelection(elements)
      selection.set('isHelper', true)
      $_addDebugListenters(selection, 'Object')
      p.$canvas.setActiveObject(selection)
    }
    p.$canvas.requestRenderAll()
    // Set the size of the whiteboard canvas
    setCanvasDimensions(state)
  })

  if (state.clipboard.length > 0) {
    // Clear the current selection
    const selection = p.$canvas.getActiveObject()
    if (selection.type === FABRIC_MULTIPLE_SELECT_TYPE) {
      p.$canvas.remove(selection)
    }
    p.$canvas.discardActiveObject().requestRenderAll()

    // Duplicate each copied element. In order to do this, remove
    // the index and unique id from the element and alter the position
    // to ensure its visibility
    _.each(state.clipboard, (element: any) => {
      delete element.index
      delete element.uuid
      element.left += 25
      element.top += 25
      // Add the element to the whiteboard canvas
      const callback = (e: any) => {
        p.$canvas.add(e)
        p.$canvas.requestRenderAll()
        // Keep track of the added elements to allow them to be selected
        elements.push(e)
        selectPasted()
      }
      deserializeElement(state, element, callback)
    })
  }
}

const createCanvas = (options: any) => {
  const canvas = new fabric.Canvas('canvas', options)
  $_addDebugListenters(canvas, 'Canvas')
  return canvas
}

const createIText = (options: any) => {
  const iText = new fabric.IText('', options)
  $_addDebugListenters(iText, 'IText')
  return iText
}

const createShape = (shapeType: string, options: any) => {
  const shape = new fabric[shapeType](options)
  $_addDebugListenters(shape, 'Object')
  return shape
}

/**
 * Ensure that all elements are ordered as specified by the element's index attribute.
 */
const restoreLayers = (state: any) => {
  p.$canvas.getObjects().sort((elementA: any, elementB: any) => {
    return elementA.index - elementB.index
  })
  p.$canvas.requestRenderAll()
  // Set the size of the whiteboard canvas
  setCanvasDimensions(state)
}

/**
 * Persist element updates to the server
 *
 * elements: The updated elements to persist to the server
 */
const saveElementUpdates = (elements: any[], state: any) => {
  // Notify the server about the updated elements
  socket.emit('update_activity', elements)
  // Recalculate the size of the whiteboard canvas
  setCanvasDimensions(state)
}

/**
 * Persist a new element to the server
 * element: The new element to persist to the server
 */
const saveNewElement = (element: any, state: any) => {
  if (!element.get('uuid')) {
    // Add a unique id to the element
    element.set('uuid', Math.round(Math.random() * 1000000))
  }
  // Save the new element
  socket.emit('add_whiteboard_elements', {
    whiteboardElements: [{
      assetId: undefined,
      element: element.toObject()
    }],
    userId: p.$currentUser.id,
    whiteboardId: state.whiteboard.id
  })
}

/**
 * Set the width and height of the whiteboard canvas. The width of the visible
 * canvas will be the same for all users, and the canvas will be zoomed to accommodate
 * that width. By default, the size of the zoomed canvas will be the same as the size
 * of the viewport. When there are any elements on the canvas that are outside of the
 * viewport boundaries, the canvas will be enlarged to incorporate those
 */
const setCanvasDimensions = (state: any) => {
  // Zoom the canvas to accomodate the base width within the viewport
  const viewportWidth = state.viewport.clientWidth
  const ratio = viewportWidth / constants.CANVAS_BASE_WIDTH
  p.$canvas.setZoom(ratio)

  // Calculate the position of the elements that are the most right and the
  // most bottom. When all elements fit within the viewport, the canvas is
  // made the same size as the viewport. When any elements overflow the viewport,
  // the canvas is enlarged to incorporate all assets outside of the viewport
  const viewportHeight = state.viewport.clientHeight
  let maxRight = viewportWidth
  let maxBottom = viewportHeight

  p.$canvas.forEachObject((element: any) => {
    let bound = null
    if (!element.group) {
      bound = element.getBoundingRect()
    } else {
      bound = element.group.getBoundingRect()
    }
    maxRight = Math.max(maxRight, _.get(bound, 'left') + _.get(bound, 'width'))
    maxBottom = Math.max(maxBottom, _.get(bound, 'top') + _.get(bound, 'height'))
  })
  // Keep track of whether the canvas can currently be scrolled
  if (maxRight > viewportWidth || maxBottom > viewportHeight) {
    state.scrollingCanvas = true

    // Add padding when the canvas can be scrolled
    if (maxRight > viewportWidth) {
      maxRight += constants.CANVAS_PADDING
    }
    if (maxBottom > viewportHeight) {
      maxBottom += constants.CANVAS_PADDING
    }
  } else {
    state.scrollingCanvas = false
  }

  // When the entire whiteboard content should fit within
  // the screen, adjust the zoom level to make it fit
  if (state.fitToScreen) {
    // Calculate the actual unzoomed width of the whiteboard
    const realWidth = maxRight / p.$canvas.getZoom()
    const realHeight = maxBottom / p.$canvas.getZoom()
    // Zoom the canvas based on whether the height or width
    // needs the largest zoom out
    const widthRatio = viewportWidth / realWidth
    const heightRatio = viewportHeight / realHeight
    const ratio = Math.min(widthRatio, heightRatio)
    p.$canvas.setZoom(ratio)

    p.$canvas.setHeight(viewportHeight)
    p.$canvas.setWidth(viewportWidth)
  } else {
    // Adjust the value for rounding issues to prevent scrollbars
    // from incorrectly showing up
    p.$canvas.setHeight(maxBottom - 1)
    p.$canvas.setWidth(maxRight - 1)
  }
}

/**
 * Update the index of all elements to reflect their order in the
 * current whiteboard
 */
const updateLayers = (state: any): void => {
  const updates: any[] = []
  p.$canvas.forEachObject((element: any) => {
    // Only update the elements for which the stored index no longer
    // matches the current index
    if (element.index !== p.$canvas.getObjects().indexOf(element)) {
      element.index = p.$canvas.getObjects().indexOf(element)
      // If the element is part of a group, calculate its global coordinates
      if (element.group) {
        const position = calculateGlobalElementPosition(element.group, element)
        updates.push(_.assignTo({}, element.toObject(), position))
      } else {
        updates.push(element.toObject())
      }
    }
  })
  // Notify the server about the updated layers
  if (updates.length > 1) {
    saveElementUpdates(updates, state)
  }
}

export default {
  addAsset,
  createCanvas,
  createIText,
  createShape,
  deleteActiveElements,
  deserializeElement,
  enableCanvasElements,
  ensureWithinCanvas,
  getActiveElements,
  getCanvasElement,
  init,
  paste,
  restoreLayers,
  saveElementUpdates,
  saveNewElement,
  setCanvasDimensions,
  updateLayers
}

/**
 * Calculate the top left position of an element in a group
 *
 * @param  {Object}         selection         The selection (group of objects) of which the element is a part
 * @param  {Object}         element           The Fabric.js element for which the top left position in its group should be calculated
 * @return {Object}                           The top left position of the element in its group. Will return the `top` and `left` postion
 */
const $_calculateRotatedLeftTop = (selection: any, element: any): any => {
  const groupAngle = selection.getAngle() * (Math.PI / 180)
  const left = (-Math.sin(groupAngle) * element.getTop() * selection.get('scaleY') + Math.cos(groupAngle) * element.getLeft() * selection.get('scaleX'))
  const top = (Math.cos(groupAngle) * element.getTop() * selection.get('scaleY') + Math.sin(groupAngle) * element.getLeft() * selection.get('scaleX'))
  return {left, top}
}

/**
 * Persist element deletions to the server
 * @param  {Object[]}       elements          The deleted elements to persist to the server
 */
const $_saveDeleteElements = (elements: any[], state: any): any => {
  // Notify the server about the deleted elements
  socket.emit('deleteActivity', elements)
  // Update the layer ordering of the remaining elements
  updateLayers(state)
  // Recalculate the size of the whiteboard canvas
  setCanvasDimensions(state)
}

const FABRIC_OBJECT_EVENTS = ['event:added', 'event:deselected', 'event:dragenter', 'event:dragleave', 'event:dragover', 'event:drop', 'event:modified', 'event:modified', 'event:mousedblclick', 'event:mousedown', 'event:mouseout', 'event:mouseover', 'event:mouseup', 'event:mousewheel', 'event:moved', 'event:moving', 'event:removed', 'event:rotated', 'event:rotating', 'event:scaled', 'event:scaling', 'event:selected', 'event:skewed', 'event:skewing']

const EVENTS_BY_FABRIC_TYPE = {
  Canvas: FABRIC_OBJECT_EVENTS.concat(['after:render', 'before:render', 'before:selection:cleared', 'before:transform', 'canvas:cleared', 'drop:before', 'mouse:dblclick', 'mouse:down:before', 'mouse:down', 'mouse:move:before', 'mouse:move', 'mouse:out', 'mouse:over', 'mouse:up:before', 'mouse:up', 'object:added', 'object:modified', 'object:moving', 'object:removed', 'object:rotating', 'object:scaling', 'object:skewing', 'path:created', 'selection:cleared', 'selection:created', 'selection:updated']),
  IText: FABRIC_OBJECT_EVENTS.concat(['event:changed', 'selection:changed', 'editing:entered', 'editing:exited']),
  Object: FABRIC_OBJECT_EVENTS
}

export function $_addDebugListenters(fabricObject: any, objectType: string) {
  if (p.$config.isVueAppDebugMode) {
    console.log(`fabric.${objectType}, add debug listenters: ${JSON.stringify(fabricObject)}`)
    _.each(EVENTS_BY_FABRIC_TYPE[objectType], (eventName: string) => {
      fabricObject.on(eventName, (event: any) => console.log({
        fabric: objectType,
        eventName,
        type: _.get(event, 'e.type'),
        event
      }))
    })
  }
}
