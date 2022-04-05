import _ from 'lodash'
import apiUtils from '@/api/api-utils'
import constants from '@/store/whiteboarding/constants'
import FABRIC_MULTIPLE_SELECT_TYPE from '@/store/whiteboarding/constants'
import store from '@/store'
import Vue from 'vue'
import {io} from 'socket.io-client'
import {fabric} from 'fabric'

const p = Vue.prototype

export function initialize(state: any, whiteboard: any) {
  if (!whiteboard.deletedAt) {
    $_initSocket(state, whiteboard)
  }
  // The whiteboard p.$canvas should be initialized only after our additions are made to Fabric prototypes.
  $_initFabricPrototypes(state)
  $_initCanvas(state)
  $_addModalListeners()
  $_addViewportListeners(state)
}
/**
 * Add an asset to the whiteboard canvas
 * asset: The asset that should be added to the whiteboard canvas
 */
 export function addAsset(asset: any, state: any) {
  // Switch the toolbar back to move mode
  store.dispatch('whiteboarding/setMode', 'move')

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
    asset.imageUrl = `${apiUtils.apiBaseUrl()}/assets/${asset.id}/download`
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
 * Delete the selected whiteboard element(s)
 */
export function deleteActiveElements(state: any) {
  // Get the selected items
  const elements = getActiveElements()
  // Delete the selected items
  console.log('delete-active-elements')
  _.each(elements, (element: any) => p.$canvas.remove(getCanvasElement(element.uuid)))
  // If a group selection was made, remove the group as well in case Fabric doesn't clean up after itself
  const selection = p.$canvas.getActiveObject()
  if (selection.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
    p.$canvas.remove(selection)
    p.$canvas.discardActiveObject().requestRenderAll()
  }
  $_saveDeleteElements(elements, state)
}

export function enableCanvasElements(enabled: boolean) {
  // Enable or disable elements on the canvas. Disabled elements are read-only.
  p.$canvas.selection = enabled
  _.each(p.$canvas.getObjects(), (element: any) => element.selectable = enabled)
}

export function getActiveElements() {
  // Get the currently selected whiteboard elements
  // return the selected whiteboard elements
  const activeElements: any[] = []
  const selection = p.$canvas.getActiveObject()
  if (_.get(selection, 'type') === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
    _.each(selection.objects, (element: any) => {
      // When a Fabric.js canvas element is part of a group selection, its properties will be
      // relative to the group. Therefore, we calculate the actual position of each element in
      // the group relative to the whiteboard canvas
      const position = $_calculateGlobalElementPosition(selection, element)
      activeElements.push(_.assignTo({}, element.toObject(), position))
    })
  } else if (p.$canvas.getActiveObject()) {
    activeElements.push(p.$canvas.getActiveObject().toObject())
  }
  return activeElements
}

export function getCanvasElement(uuid: string) {
  let element = undefined
  _.each(p.$canvas.getObjects(), (e: any) => {
    if (e.get('uuid') === uuid) {
      element = e
      return false
    }
  })
  return element
}

export function saveElementUpdates(elements: any[], state: any) {
  const whiteboardElements = _.map(elements, (element: any) => ({element}))
  p.$socket.emit('update', {
    userId: p.$currentUser.id,
    whiteboardElements,
    whiteboardId: state.whiteboard.id
  })
  setCanvasDimensions(state)
}

/**
 * Set the width and height of the whiteboard canvas. The width of the visible
 * canvas will be the same for all users, and the canvas will be zoomed to accommodate
 * that width. By default, the size of the zoomed canvas will be the same as the size
 * of the viewport. When there are any elements on the canvas that are outside of the
 * viewport boundaries, the canvas will be enlarged to incorporate those
 */
export function setCanvasDimensions(state: any) {
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
    store.dispatch('whiteboarding/setIsScrollingCanvas', true)

    // Add padding when the canvas can be scrolled
    if (maxRight > viewportWidth) {
      maxRight += constants.CANVAS_PADDING
    }
    if (maxBottom > viewportHeight) {
      maxBottom += constants.CANVAS_PADDING
    }
  } else {
    store.dispatch('whiteboarding/setIsScrollingCanvas', false)
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

export function updateLayers(state: any) {
  // Update the index of all elements to reflect their order in the current whiteboard.
  const updates: any[] = []
  p.$canvas.forEachObject((element: any) => {
    // Only update the elements for which the stored index no longer
    // matches the current index
    if (element.index !== p.$canvas.getObjects().indexOf(element)) {
      element.index = p.$canvas.getObjects().indexOf(element)
      // If the element is part of a group, calculate its global coordinates
      if (element.group) {
        const position = $_calculateGlobalElementPosition(element.group, element)
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

/**
 * ---------------------------------------------------------------------------------------
 * Export functions above. Private functions below.
 * ---------------------------------------------------------------------------------------
 */

/**
 * Calculate the position of an element in a group relative to the whiteboard canvas
 *
 * @param  {Object}         selection         The selection (group of objects) of which the element is a part
 * @param  {Object}         element           The Fabric.js element for which the position relative to its group should be calculated
 * @return {Object}                           The position of the element relative to the whiteboard canvas. Will return the `angle`, `left` and `top` postion and the `scaleX` and `scaleY` scaling factors
 */
 const $_calculateGlobalElementPosition = (selection: any, element: any): any => {
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

const $_createCanvas = (options: any) => {
  const canvas = new fabric.Canvas('canvas', options)
  $_addDebugListenters(canvas, 'Canvas')
  return canvas
}

const $_createIText = (options: any) => {
  const iText = new fabric.IText('', options)
  $_addDebugListenters(iText, 'IText')
  return iText
}

const $_createShape = (shapeType: string, options: any) => {
  const shape = new fabric[shapeType](options)
  $_addDebugListenters(shape, 'Object')
  return shape
}

const $_deserializeElement = (
  state: any,
  element: any,
  uuid: string,
  callback: any
) => {
  // Convert a serialized Fabric.js canvas element to a proper Fabric.js canvas element
  // element: The serialized Fabric.js canvas element to deserialize
  // callback: Standard callback function
  element = _.cloneDeep(element)
  element.uuid = uuid
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
 * Ensure that the currently active object or group can not be positioned off screen
 *
 * event: The event representing the active object or group
 */
const $_ensureWithinCanvas = (event: any) => {
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

const $_initFabricPrototypes = (state: any) => {
  fabric.Object.prototype.toObject = (function(toObject) {
    // Extend the Fabric.js `toObject` deserialization function to include the property that
    // uniquely identifies an object on the canvas, as well as a property containing the index
    // of the object relative to the other items on the canvas.
    return function() {
      const extras = {
        assetId: this.assetId,
        height: this.height,
        index: p.$canvas.getObjects().indexOf(this),
        text: this.text,
        uuid: this.uuid,
        width: this.width
      }
      return fabric.util.object.extend(toObject.call(this), extras)
    }
  }(fabric.Object.prototype.toObject))

  fabric.IText.prototype.on('editing:exited', function() {
    // An IText whiteboard canvas element was updated by the current user.
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
        $_saveNewElement(element, state)
      } else {
        // The text element existed before. Notify the server that the element was updated
        saveElementUpdates([element], state)
      }
      store.dispatch('whiteboarding/setMode', 'move')
    }
  })
  // Recalculate the size of the p.$canvas when the window is resized
  window.addEventListener('resize', () => setCanvasDimensions(state))
}

/**
 * Paste the copied element(s)
 */
const $_paste = (state: any): void => {
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
    if (selection.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
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
      $_deserializeElement(state, element, element.uuid, callback)
    })
  }
}

const $_restoreLayers = (state: any) => {
  // Ensure that all elements are ordered as specified by the element's index attribute.
  p.$canvas.getObjects().sort((elementA: any, elementB: any) => elementA.index - elementB.index)
  p.$canvas.requestRenderAll()
  setCanvasDimensions(state)
}

const $_saveNewElement = (element: any, state: any) => {
  p.$socket.emit('add', {
    whiteboardElements: [{
      assetId: undefined,
      element: element.toObject()
    }],
    userId: p.$currentUser.id,
    whiteboardId: state.whiteboard.id
  })
}

const $_initCanvas = (state: any) => {
  // Initialize the Fabric.js canvas and load the whiteboard content and online users
  // Ensure that the horizontal and vertical origins of objects are set to center
  fabric.Object.prototype.originX = fabric.Object.prototype.originY = 'center'
  // Set the selection style for the whiteboard
  // Set the style of the multi-select helper
  Vue.prototype.$canvas = $_createCanvas({
    selectionColor: 'transparent',
    selectionBorderColor: '#0295DE',
    selectionLineWidth: 2
  })
  // Make the border dashed
  // @see http://fabricjs.com/fabric-intro-part-4/
  p.$canvas.selectionDashArray = [10, 5]

  // Set the selection style for all elements
  fabric.Object.prototype.borderColor = '#0295DE'
  fabric.Object.prototype.borderScaleFactor = 0.3
  fabric.Object.prototype.cornerColor = '#0295DE'
  fabric.Object.prototype.cornerSize = 10
  fabric.Object.prototype.transparentCorners = false
  fabric.Object.prototype.rotatingPointOffset = 30
  // Set the pencil brush as the drawing brush
  p.$canvas.freeDrawingBrush = new fabric.PencilBrush(p.$canvas)
  // Render the whiteboard
  $_addListenters(state)
  $_renderWhiteboard(state)
}

const $_initSocket = (state: any, whiteboard: any) => {
  Vue.prototype.$socket = io(apiUtils.apiBaseUrl(), {
    query: {
      whiteboardId: whiteboard.id
    }
  })
  p.$socket.on('connect', _.noop)
  p.$socket.on('disconnect', _.noop)
  p.$socket.on('error', (error: any) => store.dispatch('whiteboarding/log', `ERROR, socket.io: '${error}'`))
  p.$socket.on('online', (onlineUsers: any[]) => {
    // When a user has joined or left the whiteboard, update the online status on the list of members
    if (whiteboard) {
      for (let i = 0; i < whiteboard.members.length; i++) {
        const member = whiteboard.members[i]
        member.online = _.find(onlineUsers, {user_id: member.id}) ? true : false
      }
    }
  })
  $_addSocketListeners(state)
}

const $_addListenters = (state: any) => {
  // Indicate that the currently selected elements are in the process of being moved, scaled or rotated
  const setModifyingElement = () => store.dispatch('whiteboarding/setIsModifyingElement', true)
  p.$canvas.on('object:moving', setModifyingElement)
  p.$canvas.on('object:scaling', setModifyingElement)
  p.$canvas.on('object:rotating', setModifyingElement)
  p.$canvas.on('object:moving', (event: any) => $_ensureWithinCanvas(event))

  // One or multiple whiteboard canvas elements have been updated by the current user
  p.$canvas.on('object:modified', (event: any) => {
    // Ensure that none of the modified objects are positioned off screen
    $_ensureWithinCanvas(event)
    // Get the selected whiteboard elements
    const elements = getActiveElements()
    // Notify the server about the updates
    saveElementUpdates(elements, state)
  })

  // Indicate that the currently selected elements are no longer being modified once moving, scaling or rotating has finished
  p.$canvas.on('object:modified', () => store.dispatch('whiteboarding/setIsModifyingElement', false))

  // (1) Draw a box around the currently selected element(s) and (2) position buttons that allow the selected element(s) to be modified.
  p.$canvas.on('after:render', () => store.dispatch('whiteboarding/afterCanvasRender'))

  /**
   * When a new group has been added programmatically added, it needs to be programmatically
   * removed from the canvas when the group is deselected
   */
  p.$canvas.on('before:selection:cleared', () => {
    const selection = p.$canvas.getActiveObject()
    if (selection.type === FABRIC_MULTIPLE_SELECT_TYPE) {
      p.$canvas.remove(selection)
    }
  })

  // Recalculate the size of the whiteboard canvas when a selection has been deselected
  p.$canvas.on('selection:cleared', () => setCanvasDimensions(state))

  /**
   * A new element was added to the whiteboard canvas by the current user
   */
  p.$canvas.on('object:added', (event: any) => {
    const element = event.target
    // Don't add a new text element until text has been entered
    if (!('text' in element) || element.text.trim()) {
      // If the element already has a unique id, it was added by a different user and there is no need to persist the addition
      if (!element.get('') && !element.get('isHelper')) {
        $_saveNewElement(element, state)
        // Recalculate the size of the whiteboard canvas
        setCanvasDimensions(state)
      }
    }
  })

  /**
   * The mouse is pressed down on the whiteboard canvas
   */
   p.$canvas.on('mouse:down', (event: any) => {
    // Only start drawing a shape when the canvas is in shape mode
    if (state.mode === 'shape') {
      // Indicate that drawing a shape has started
      state.isDrawingShape = true

      // Keep track of the point where drawing the shape started
      state.startShapePointer = p.$canvas.getPointer(event.e)

      // Create the basic shape of the selected type that will
      // be used as the drawing guide. The originX and originY
      // of the helper element are set to left and top to make it
      // easier to map the top left corner of the drawing guide with
      // the original cursor postion
      const selected = state.shapeOptions.selected
      const shapeType = selected.type.shape
      const fill = selected.type.style === 'fill' ? state.shapeOptions.selected.color.color : 'transparent'
      state.shape = $_createShape(shapeType, {
        fill,
        height: 1,
        left: state.startShapePointer.x,
        originX: 'left',
        originY: 'top',
        radius: 1,
        stroke: state.shapeOptions.selected.color.color,
        strokeWidth: state.shapeOptions.selected.type.style === 'thick' ? 10 : 2,
        top: state.startShapePointer.y,
        width: 1
      })
      // Indicate that this element is a helper element that should
      // not be saved back to the server
      state.shape.set('isHelper', true)
      p.$canvas.add(state.shape)
    }
  })

  /**
   * The mouse is moved on the whiteboard canvas
   */
  p.$canvas.on('mouse:move', (event: any) => {
    // Only continue drawing the shape when the whiteboard canvas is in shape mode
    if (state.isDrawingShape) {
      // Get the current position of the mouse
      const currentShapePointer = p.$canvas.getPointer(event.e)

      // When the user has moved the cursor to the left of the original
      // starting point, move the left of the circle to that point so
      // negative shape drawing can be achieved
      if (state.startShapePointer.x > currentShapePointer.x) {
        state.shape.set({left: currentShapePointer.x})
      }
      // When the user has moved the cursor above the original starting
      // point, move the left of the circle to that point so negative
      // shape drawing can be achieved
      if (state.startShapePointer.y > currentShapePointer.y) {
        state.shape.set({top: currentShapePointer.y})
      }

      // Set the radius and width of the circle based on how much the cursor
      // has moved compared to the starting point
      if (state.shapeOptions.selected.type.shape === 'Circle') {
        state.shape.set({
          height: Math.abs(state.startShapePointer.x - currentShapePointer.x),
          radius: Math.abs(state.startShapePointer.x - currentShapePointer.x) / 2,
          width: Math.abs(state.startShapePointer.x - currentShapePointer.x)
        })
      // Set the width and height of the shape based on how much the cursor
      // has moved compared to the starting point
      } else {
        state.shape.set({
          height: Math.abs(state.startShapePointer.y - currentShapePointer.y),
          width: Math.abs(state.startShapePointer.x - currentShapePointer.x)
        })
      }
      p.$canvas.requestRenderAll()
    }
  })

  /**
   * The mouse is released on the whiteboard canvas
   */
  p.$canvas.on('mouse:up', () => {
    if (state.isDrawingShape) {
      // Indicate that shape drawing has stopped
      state.isDrawingShape = false
      // Switch the toolbar back to move mode
      state.mode = 'move'
      // Clone the drawn shape and add the clone to the canvas.
      // This is caused by a bug in Fabric where it initially uses
      // the size when drawing started to position the controls. Cloning
      // ensures that the controls are added in the correct position.
      // The origin of the element is also set to `center` to make it
      // inline with the other whiteboard elements
      const finalShape = fabric.util.object.clone(state.shape)
      finalShape.left += finalShape.width / 2
      finalShape.top += finalShape.height / 2
      finalShape.originX = finalShape.originY = 'center'
      // Indicate that this is no longer a drawing helper shape and can
      // therefore be saved back to the server
      finalShape.set('isHelper', false)

      p.$canvas.add(finalShape)
      p.$canvas.remove(state.shape)
      // Select the added shape
      p.$canvas.setActiveObject(finalShape)
    }
  })

  p.$canvas.on('mouse:down', (event: any) => {
    if (state.mode === 'text') {
      const textPointer = p.$canvas.getPointer(event.e)
      const text = $_createIText({
        backgroundColor: 'red',
        fill: state.selected.fill,
        fontFamily: '"HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif',
        fontSize: state.selected.fontSize || 14,
        height: 100, // TODO
        left: textPointer.x,
        text: 'TODO: Hello World',
        selectable: true,
        selected: true,
        top: textPointer.y
      })
      p.$canvas.add(text)

      // Put the editable text field in edit mode straight away
      setTimeout(function() {
        p.$canvas.setActiveObject(text)
        text.enterEditing()
        // The textarea needs to be put in edit mode manually
        // @see https://github.com/kangax/fabric.js/issues/1740
        text.hiddenTextarea.focus()
      }, 0)
    }
  })

  p.$canvas.on('selection:created', () => store.dispatch('whiteboarding/setActiveCanvasObject', p.$canvas.getActiveObject()))
  p.$canvas.on('selection:cleared', () => store.dispatch('whiteboarding/setActiveCanvasObject', null))
  p.$canvas.on('selection:updated', () => store.dispatch('whiteboarding/setActiveCanvasObject', p.$canvas.getActiveObject()))
}

const $_renderWhiteboard = (state: any) => {
  // Render the whiteboard and its elements
  // Set the size of the whiteboard canvas once all layout changes
  // regarding the sidebar have been applied
  setTimeout(() => setCanvasDimensions(state), 0)

  // Restore the order of the layers once all elements have finished loading
  const restore = _.after(state.whiteboard.whiteboardElements.length, () => {
    $_restoreLayers(state)
    // Deactivate all elements and element selection when the whiteboard
    // is being rendered in read only mode
    if (state.whiteboard.deletedAt) {
      p.$canvas.discardActiveObject()
      p.$canvas.selection = false
    }
  })
  // Restore the layout of the whiteboard canvas
  _.each(state.whiteboard.whiteboardElements, (element: any) => {
    $_deserializeElement(state, element.element, element.uuid, (e: any) => {
      p.$canvas.add(e)
      restore()
    })
  })
}

const $_addModalListeners = () => {
  // TODO: Set the toolbar back to move mode when the asset and export tooltips are hidden.
  // state.$on('tooltip.hide', function(ev, $tooltip) {
  //   if ((state.mode === 'asset' && $tooltip.$id === 'whiteboards-board-asset-trigger') || (state.mode === 'export' && $tooltip.$id === 'whiteboards-board-export-trigger')) {
  //     state.mode = 'move'
  //   }
  // })
  // // Change the drawing color when a new color has been selected in the color picker
  // state.$watch('draw.selected.color', () => p.$canvas.freeDrawingBrush.color = state.draw.selected.color.color, true)
  // // Change the drawing line width when a new line width has been selected in the width picker
  // state.$watch('draw.selected.lineWidth', () => p.$canvas.freeDrawingBrush.width = parseInt(state.draw.selected.lineWidth, 10), true)
}

/**
 * Detect keydown events in the whiteboard to respond to keyboard shortcuts
 */
const $_addViewportListeners = (state: any) => {
  state.viewport.addEventListener('keydown', (event: any) => {
    // Remove the selected elements when the delete or backspace key is pressed
    if (event.keyCode === 8 || event.keyCode === 46) {
      deleteActiveElements(state)
      event.preventDefault()
    } else if (event.keyCode === 67 && event.metaKey) {
      // Copy the selected elements
      state.clipboard = getActiveElements()
    } else if (event.keyCode === 86 && event.metaKey) {
      // listeners.Paste the copied elements
      $_paste(state)
    }
  }, false)
}


const $_addSocketListeners = (state: any) => {
  /**
   * One or multiple whiteboard canvas elements were updated by a different user
   */
   p.$socket.on('update', (elements: any) => {
    // Deactivate the current group if any of the updated elements are in the current group
    $_deactiveActiveGroupIfOverlap(elements)
    // Update the elements
    _.each(elements, function(element) {
      $_updateCanvasElement(state, element.uuid, element)
    })
    // Recalculate the size of the whiteboard canvas
    setCanvasDimensions(state)
  })
  /**
   * A whiteboard canvas element was added by a different user
   */
   p.$socket.on('add', (elements: any[]) => {
    _.each(elements, (element: any) => {
      const callback = (e: any) => {
        // Add the element to the whiteboard canvas and move it to its appropriate index
        p.$canvas.add(e)
        element.moveTo(e.get('index'))
        p.$canvas.requestRenderAll()
        // Recalculate the size of the whiteboard canvas
        setCanvasDimensions(state)
      }
      $_deserializeElement(state, element, element.uuid, callback)
    })
  })

  /**
   * One or multiple whiteboard canvas elements were deleted by a different user
   */
   p.$socket.on('delete', (elements: any[]) => {
    // Deactivate the current group if any of the deleted elements are in the current group
    $_deactiveActiveGroupIfOverlap(elements)
    // Delete the elements
    _.each(elements, function(element) {
      element = getCanvasElement(element.uuid)
      if (element) {
        p.$canvas.remove(element)
      }
    })
    // Recalculate the size of the whiteboard canvas
    setCanvasDimensions(state)
  })
}

/**
 * CONCURRENT EDITING
 * Deactivate the active group if any of the provided elements are a part of the active group
 * elements: The elements that should be checked for presence in the active group
 */
 const $_deactiveActiveGroupIfOverlap = (elements: any[]) => {
  const selection = p.$canvas.getActiveObject()
  if (selection.type === FABRIC_MULTIPLE_SELECT_TYPE) {
    const intersection = _.intersection(_.map(selection.objects, 'uuid'), _.map(elements, 'uuid'))
    if (intersection.length > 0) {
      p.$canvas.discardActiveGroup().requestRenderAll()
    }
  }
}

/**
 * Update the appearance of a Fabric.js canvas element
 *
 * @param  {Number}         uuid               The id of the element to update
 * @param  {Object}         update            The updated values to apply to the canvas element
 */
 const $_updateCanvasElement = (state: any, uuid: string, update: any) => {
  const element: any = getCanvasElement(uuid)

  const updateElementProperties = () => {
    if (element) {
      // Update all element properties, except for the image source. The image
      // source is handled separately as this is an asynchronous action
      _.each(update, function(value, property) {
        if (property !== 'src' && value !== element.get(property)) {
          element.set(property, value)
        }
      })
      // When the source element for an asset has changed, update this last and
      // re-render the element after it has been loaded
      if (element.type === 'image' && element.getSrc() !== update.src) {
        element.setSrc(update.src, () => {
          p.$canvas.requestRenderAll()
          // Ensure that the correct position is applied
          $_restoreLayers(state)
        })
      } else {
        $_restoreLayers(state)
      }
    }
  }
  // If the element is an asset for which the source has changed, we preload
  // the image to prevent flickering when the image is inserted into the element
  if (element.type === 'image' && element.getSrc() !== update.src) {
    fabric.util.loadImage(update.src, updateElementProperties)
  } else {
    updateElementProperties()
  }
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
  p.$socket.emit('delete', elements)
  // Update the layer ordering of the remaining elements
  updateLayers(state)
  // Recalculate the size of the whiteboard canvas
  setCanvasDimensions(state)
}

export function $_addDebugListenters(fabricObject: any, objectType: string) {
  if (p.$config.isVueAppDebugMode) {
    // Events listed in FABRIC_JS_DEBUG_EVENTS_EXCLUDE array are ignored when debugging. Developers can silence these
    // debug-event-listenters by setting FABRIC_JS_DEBUG_EVENTS_EXCLUDE equal to '*' in the .env.development.local file.
    const exclude = constants.FABRIC_JS_DEBUG_EVENTS_EXCLUDE
    if (exclude !== '*') {
      let eventNames = constants.FABRIC_EVENTS_PER_TYPE[objectType]
      eventNames = _.filter(eventNames, (eventName: string) => !exclude.includes(eventName))
      _.each(eventNames, (eventName: string) => fabricObject.on(eventName, () => console.log(`${objectType}:${eventName}`)))
    }
  }
}
