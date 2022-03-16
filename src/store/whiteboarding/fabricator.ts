import _ from 'lodash'
import {fabric} from 'fabric'
import constants from '@/store/whiteboarding/constants'
import utils from '@/api/api-utils'
import Vue from 'vue'

const p = Vue.prototype

/**
 * Add an asset to the whiteboard canvas
 * asset: The asset that should be added to the whiteboard canvas
 */
const addAsset = (asset: any, state: any) => {
  // Switch the toolbar back to move mode
  state.mode = 'move'

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
  fabric.Image.fromURL(imageUrl, function(element) {
    // This will exclude the toolbar and the chat/online sidebar (if expanded)
    // Calculate the center point of the whiteboard canvas
    const zoomLevel = p.$canvas.getZoom()
    const centerX = ((state.viewport.clientWidth / 2) + state.viewport.scrollLeft) / zoomLevel
    const centerY = ((state.viewport.clientHeight / 2) + state.viewport.scrollTop) / zoomLevel

    const canvasCenter = {
      x: centerX,
      y: centerY
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
 * @param  {Object}         group             The group of which the element is a part
 * @param  {Object}         element           The Fabric.js element for which the position relative to its group should be calculated
 * @return {Object}                           The position of the element relative to the whiteboard canvas. Will return the `angle`, `left` and `top` postion and the `scaleX` and `scaleY` scaling factors
 */
const calculateGlobalElementPosition = (group: any, element: any): any => {
  const center = group.getCenterPoint()
  const rotated = $_calculateRotatedLeftTop(group, element)
  return {
    'angle': element.getAngle() + group.getAngle(),
    'left': center.x + rotated.left,
    'top': center.y + rotated.top,
    'scaleX': element.get('scaleX') * group.get('scaleX'),
    'scaleY': element.get('scaleY') * group.get('scaleY')
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
  // If a group selection was made, remove the group as well
  // in case Fabric doesn't clean up after itself
  if (p.$canvas.getActiveGroup()) {
    p.$canvas.remove(p.$canvas.getActiveGroup())
    p.$canvas.deactivateAll().requestRenderAll()
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
    fabric[type].fromObject(element, function(e) {
      e.setSrc(e.get('realSrc'), function() {
        return callback(e)
      })
    })
  } else if (fabric[type].async) {
    fabric[type].fromObject(element, callback)
  } else {
    return callback(fabric[type].fromObject(element))
  }
}

/**
 * Enable or disable all elements on the whiteboard canvas. When an element is disabled, it will not be possible
 * to select, move or modify it
 *
 * enabled: Whether the elements on the whiteboard canvas should be enabled or disabled
 */
const enableCanvasElements = (enabled: boolean) => {
  p.$canvas.selection = enabled
  const elements = p.$canvas.getObjects()
  for (let i = 0; i < elements.length; i++) {
    elements[i].selectable = enabled
  }
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

const extendFabricObjects = (state: any) => {
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
        'uuid': object.uuid,
        'index': p.$canvas.getObjects().indexOf(object),
        'assetId': object.assetId,
        'width': object.width,
        'height': object.height
      })
    }
  }(fabric.Object.prototype.toObject))

  /**
   * An IText whiteboard canvas element was updated by the current user
   */
  fabric.IText.prototype.on('editing:exited', () => {
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
        saveNewElement(element)
      } else {
        // The text element existed before. Notify the server that the element was updated
        saveElementUpdates([element], state)
      }
      state.mode = 'move'
    }
  })
}

const getActiveElements = (): any[] => {
  // Get the currently selected whiteboard elements
  // return the selected whiteboard elements
  const activeElements: any[] = []
  const group = p.$canvas.getActiveGroup()
  if (group) {
    _.each(group.objects, function(element) {
      // When a Fabric.js canvas element is part of a group selection, its properties will be
      // relative to the group. Therefore, we calculate the actual position of each element in
      // the group relative to the whiteboard canvas
      const position = calculateGlobalElementPosition(group, element)
      activeElements.push(_.assignTo({}, element.toObject(), position))
    })
  } else if (p.$canvas.getActiveObject()) {
    activeElements.push(p.$canvas.getActiveObject().toObject())
  }
  return activeElements
}

const getCanvasElement = (uuid: number) => {
  const elements = p.$canvas.getObjects()
  for (let i = 0; i < elements.length; i++) {
    if (elements[i].get('uuid') === uuid) {
      return elements[i]
    }
  }
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
      const group = new fabric.Group()
      group.set('isHelper', true)
      p.$canvas.add(group)
      _.each(elements, function(element) {
        group.addWithUpdate(element)
      })
      p.$canvas.setActiveGroup(group)
    }
    p.$canvas.requestRenderAll()
    // Set the size of the whiteboard canvas
    setCanvasDimensions(state)
  })

  if (state.clipboard.length > 0) {
    // Clear the current selection
    if (p.$canvas.getActiveGroup()) {
      p.$canvas.remove(p.$canvas.getActiveGroup())
    }
    p.$canvas.deactivateAll().requestRenderAll()

    // Duplicate each copied element. In order to do this, remove
    // the index and unique id from the element and alter the position
    // to ensure its visibility
    _.each(state.clipboard, function(element) {
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
  p.$socket.emit('updateActivity', elements)
  // Recalculate the size of the whiteboard canvas
  setCanvasDimensions(state)
}

/**
 * Persist a new element to the server
 * element: The new element to persist to the server
 */
const saveNewElement = (element: any) => {
  if (!element.get('uuid')) {
    // Add a unique id to the element
    element.set('uuid', Math.round(Math.random() * 1000000))
  }
  // Save the new element
  p.$socket.emit('addActivity', [element.toObject()])
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
  deleteActiveElements,
  deserializeElement,
  enableCanvasElements,
  ensureWithinCanvas,
  extendFabricObjects,
  getActiveElements,
  getCanvasElement,
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
 * @param  {Object}         group             The group of which the element is a part
 * @param  {Object}         element           The Fabric.js element for which the top left position in its group should be calculated
 * @return {Object}                           The top left position of the element in its group. Will return the `top` and `left` postion
 */
const $_calculateRotatedLeftTop = (group: any, element: any): any => {
  const groupAngle = group.getAngle() * (Math.PI / 180)
  const left = (-Math.sin(groupAngle) * element.getTop() * group.get('scaleY') + Math.cos(groupAngle) * element.getLeft() * group.get('scaleX'))
  const top = (Math.cos(groupAngle) * element.getTop() * group.get('scaleY') + Math.sin(groupAngle) * element.getLeft() * group.get('scaleX'))
  return {
    'left': left,
    'top': top
  }
}

/**
 * Persist element deletions to the server
 * @param  {Object[]}       elements          The deleted elements to persist to the server
 */
const $_saveDeleteElements = (elements: any[], state: any): any => {
  // Notify the server about the deleted elements
  p.$socket.emit('deleteActivity', elements)
  // Update the layer ordering of the remaining elements
  updateLayers(state)
  // Recalculate the size of the whiteboard canvas
  setCanvasDimensions(state)
}
