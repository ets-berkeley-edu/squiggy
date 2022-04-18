import _ from 'lodash'
import apiUtils from '@/api/api-utils'
import constants from '@/store/whiteboarding/constants'
import store from '@/store'
import Vue from 'vue'
import {io} from 'socket.io-client'
import {fabric} from 'fabric'

const p = Vue.prototype

export function addAsset(asset: any, state: any) {
  // Switch the toolbar back to move mode
  store.dispatch('whiteboarding/setMode', 'move')

  // Default to a placeholder when the asset does not have a preview image
  let imageUrl: any = undefined
  if (asset.imageUrl && asset.imageUrl.match(new RegExp(p.$config.s3PreviewUrlPattern))) {
    imageUrl = asset.imageUrl
  } else {
    const isImageFile = asset.assetType === 'file' && asset.mime.indexOf('image/') !== -1
    imageUrl = isImageFile ? asset.downloadUrl : constants.ASSET_PLACEHOLDERS[asset.assetType]
  }
  // Add the asset to the center of the whiteboard canvas
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

export function deleteActiveElements(state: any) {
  const elements = $_getActiveObjects()
  _.each(elements, (element: any) => p.$canvas.remove($_getCanvasElement(element.uuid)))
  // If a group selection was made, remove the group as well in case Fabric doesn't clean up after itself
  const activeObject = p.$canvas.getActiveObject()
  if (activeObject) {
    if (activeObject.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
      p.$canvas.remove(activeObject)
      p.$canvas.discardActiveObject().requestRenderAll()
    }
  }
  $_saveDeleteElements(elements, state)
}

export function enableCanvasElements(enabled: boolean) {
  // Enable or disable elements on the canvas. Disabled elements are read-only.
  p.$canvas.selection = enabled
  _.each(p.$canvas.getObjects(), (element: any) => element.selectable = enabled)
}

export function initFabricCanvas(state: any, whiteboard: any) {
  if (!whiteboard.deletedAt) {
    $_initSocket(state, whiteboard)
    $_addSocketListeners(state)
  }
  // The whiteboard p.$canvas should be initialized only after our additions are made to Fabric prototypes.
  $_initFabricPrototypes(state)
  $_initCanvas(state)
  $_addViewportListeners(state)
}

export function moveLayer(direction: string, state: any) {
  // Send the currently selected element(s) to the back or  bring the currently selected element(s) to the front.
  // direction: `front` if the currently selected element(s) should be brought to the front,
  // `back` if the currently selected element(s) should be sent to the back
  const elements: any[] = $_getActiveObjects()

  // Sort the selected elements by their position to ensure that
  // they are in the same order when moved to the back or front
  elements.sort((elementA: any, elementB: any) => direction === 'back' ? elementB.index - elementA.index : elementA.index - elementB.index)

  const selection = p.$canvas.getActiveObject()
  if (selection.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
    p.$canvas.remove(selection)
  }

  p.$canvas.discardActiveObject().requestRenderAll()
  _.each(elements, (e: any) => {
    const element:any = $_getCanvasElement(e.uuid)
    if (element) {
      if (direction === 'back') {
        p.$canvas.sendToBack(element)
      } else if (direction === 'front') {
        p.$canvas.bringToFront(element)
      }
    }
  })
  // Notify the server about the updated layers
  $_updateLayers(state)

  if (elements.length === 1) {
    // When only a single item was selected, re-select it
    p.$canvas.setActiveObject($_getCanvasElement(elements[0].uuid))
  }
}

export function onWhiteboardUpdate(state: any, whiteboard: any) {
  _.assignIn(state.whiteboard, whiteboard)
  document.title = `${whiteboard.title} | SuiteC`
  p.$socket.emit('update_whiteboard', {
    ...$_getUserSession(state),
    ...{
      title: whiteboard.title,
      users: whiteboard.users
    }
  })
  if (!p.$currentUser.isAdmin && !p.$currentUser.isTeaching) {
    const userIds = _.map(whiteboard.users, 'id')
    if (!_.includes(userIds, p.$currentUser.id)) {
      window.close()
    }
  }
}

export function ping(state: any) {
  p.$socket.emit(
    'ping',
    $_getUserSession(state),
    (users: any[]) => store.dispatch('whiteboarding/setUsers', users),
  )
}

export function setCanvasDimensions(state: any) {
  // Set the width and height of the whiteboard canvas. The width of the visible
  // canvas will be the same for all users, and the canvas will be zoomed to accommodate
  // that width. By default, the size of the zoomed canvas will be the same as the size
  // of the viewport. When there are any elements on the canvas that are outside of the
  // viewport boundaries, the canvas will be enlarged to incorporate those.

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

/**
 * ---------------------------------------------------------------------------------------
 * Public functions above. Private functions below.
 * ---------------------------------------------------------------------------------------
 */

const $_addDebugListenters = (fabricObject: any, objectType: string) => {
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
    $_saveElementUpdates($_getActiveObjects(), state)
  })

  // Indicate that the currently selected elements are no longer being modified once moving, scaling or rotating has finished
  p.$canvas.on('object:modified', () => store.dispatch('whiteboarding/setIsModifyingElement', false))

  // (1) Draw a box around the currently selected element(s) and (2) position buttons that allow the selected element(s) to be modified.
  p.$canvas.on('after:render', () => {
    const selection = p.$canvas.getActiveObject()
    if (selection && !state.isModifyingElement) {
      // Get the bounding rectangle around the currently selected element(s)
      const bound = selection.getBoundingRect()
      if (bound) {
        // Explicitly draw the bounding rectangle
        p.$canvas.contextContainer.strokeStyle = '#0295DE'
        p.$canvas.contextContainer.strokeRect(bound.left - 10, bound.top - 10, bound.width + 20, bound.height + 20)
      }
      // Position the buttons to modify the selected element(s)
      const editButtons = document.getElementById('whiteboard-element-edit')
      if (editButtons) {
        editButtons.style.left = (bound.left - 10) + 'px'
        editButtons.style.top = (bound.top + bound.height + 15) + 'px'
      }
    }
  })

  /**
   * When a new group has been added programmatically added, it needs to be programmatically
   * removed from the canvas when the group is deselected
   */
  p.$canvas.on('before:selection:cleared', () => {
    const selection = p.$canvas.getActiveObject()
    if (selection.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
      p.$canvas.remove(selection)
    }
  })

  // Recalculate the size of the whiteboard canvas when a selection has been deselected
  p.$canvas.on('selection:cleared', () => setCanvasDimensions(state))

  p.$canvas.on('object:added', (event: any) => {
    // A new element was added to the whiteboard canvas by the current user
    const element = event.target
    const isIncompleteIText = element.type === 'i-text' && !element.text.trim()
    // If the element already has a unique id, it was added by a different user and there is no need to persist the addition
    if (!isIncompleteIText && !element.get('uuid') && !element.isHelper) {
      $_saveNewElement(element, state)
      setCanvasDimensions(state)
    }
  })

  p.$canvas.on('mouse:down', (event: any) => {
    if (state.mode === 'shape') {
      store.dispatch('whiteboarding/setIsDrawingShape', true)
      // Keep track of the point where drawing the shape started
      store.dispatch('whiteboarding/setStartShapePointer', p.$canvas.getPointer(event.e))

      // Create selected shape to use as the drawing guide. The originX and originY of the helper element are set to
      // left and top to make it easier to map the top left corner of the drawing guide with the original cursor postion.
      // We use 'isHelper' to indicate that this element is a helper element that should not be saved back to the server.
      const shape = new fabric[state.selected.shape]({
        fill: state.selected.fill,
        height: 1,
        isHelper: true,
        left: state.startShapePointer.x,
        originX: 'left',
        originY: 'top',
        radius: 1,
        stroke: state.selected.color,
        strokeWidth: state.selected.strokeWidth,
        top: state.startShapePointer.y,
        width: 1
      })
      $_addDebugListenters(shape, 'Object')
      p.$canvas.add(shape)
    }
    if (state.mode === 'text') {
      const textPointer = p.$canvas.getPointer(event.e)
      const iText = new fabric.IText('', {
        fill: state.selected.fill,
        fontFamily: '"HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif',
        fontSize: state.selected.fontSize || 14,
        height: 100, // TODO
        left: textPointer.x,
        text: '',
        selectable: true,
        selected: true,
        top: textPointer.y
      })
      $_addDebugListenters(iText, 'IText')
      p.$canvas.add(iText)

      // Put the editable text field in edit mode straight away
      setTimeout(function() {
        p.$canvas.setActiveObject(iText)
        iText.enterEditing()
        // The textarea needs to be put in edit mode manually
        // @see https://github.com/kangax/fabric.js/issues/1740
        iText.hiddenTextarea.focus()
      }, 0)
    }
  })
  p.$canvas.on('mouse:move', (event: any) => {
    // Only continue drawing the shape when the whiteboard canvas is in shape mode
    if (state.isDrawingShape) {
      const shape = $_getHelperObject()
      // Get the current position of the mouse
      const currentShapePointer = p.$canvas.getPointer(event.e)

      // When the user has moved the cursor to the left of the original
      // starting point, move the left of the circle to that point so
      // negative shape drawing can be achieved
      if (state.startShapePointer.x > currentShapePointer.x) {
        shape.set({left: currentShapePointer.x})
      }
      // When the user has moved the cursor above the original starting
      // point, move the left of the circle to that point so negative
      // shape drawing can be achieved
      if (state.startShapePointer.y > currentShapePointer.y) {
        shape.set({top: currentShapePointer.y})
      }

      // Set the radius and width of the circle based on how much the cursor
      // has moved compared to the starting point
      if (state.selected.shape === 'Circle') {
        shape.set({
          height: Math.abs(state.startShapePointer.x - currentShapePointer.x),
          radius: Math.abs(state.startShapePointer.x - currentShapePointer.x) / 2,
          width: Math.abs(state.startShapePointer.x - currentShapePointer.x)
        })
      // Set the width and height of the shape based on how much the cursor
      // has moved compared to the starting point
      } else {
        shape.set({
          height: Math.abs(state.startShapePointer.y - currentShapePointer.y),
          width: Math.abs(state.startShapePointer.x - currentShapePointer.x)
        })
      }
      p.$canvas.requestRenderAll()
    }
  })

  p.$canvas.on('mouse:up', () => {
    if (state.isDrawingShape) {
      const shape = $_getHelperObject()
      // Indicate that shape drawing has stopped
      store.dispatch('whiteboarding/setIsDrawingShape', false)
      store.dispatch('whiteboarding/setMode', 'move')
      // Clone the drawn shape and add the clone to the canvas.
      // This is caused by a bug in Fabric where it initially uses
      // the size when drawing started to position the controls. Cloning
      // ensures that the controls are added in the correct position.
      // The origin of the element is also set to `center` to make it
      // inline with the other whiteboard elements
      if (shape) {
        shape.left += shape.width / 2
        shape.top += shape.height / 2
        shape.originX = shape.originY = 'center'
        // Indicate that this is no longer a drawing helper shape and can therefore be saved back to the server
        shape.isHelper = false

        // TODO: why was it done like this in old SuiteC?
        // p.$canvas.add(finalShape)
        // p.$canvas.remove(state.shape)

        // Save the added shape and make it active.
        $_saveNewElement(shape, state)
        p.$canvas.setActiveObject(shape)
      }
    }
  })
  p.$canvas.on('selection:created', () => store.dispatch('whiteboarding/setActiveCanvasObject', p.$canvas.getActiveObject()))
  p.$canvas.on('selection:cleared', () => store.dispatch('whiteboarding/setActiveCanvasObject', null))
  p.$canvas.on('selection:updated', () => store.dispatch('whiteboarding/setActiveCanvasObject', p.$canvas.getActiveObject()))
}

const $_addSocketListeners = (state: any) => {
  const onWindowClose = (event: any) => {
    if (p.$socket && p.$socket.connected) {
      p.$socket.emit('leave', $_getUserSession(state))
      p.$socket.disconnect()
    }
    if (event) {
      event.preventDefault()
    }
  }
  window.onbeforeunload = onWindowClose
  window.onunload = onWindowClose

  p.$socket.on('join', (data: any) => {
    if ($_isSocketCallbackRelevant(data, state)) {
      store.dispatch('whiteboarding/setUsers', data.users)
    }
  })
  p.$socket.on('leave', (data: any) => {
    if ($_isSocketCallbackRelevant(data, state)) {
      store.dispatch('whiteboarding/setUsers', data.users)
    }
  })

  // One or multiple whiteboard canvas elements were updated by a different user
  p.$socket.on('update_whiteboard', (data: any) => {
    if ($_isSocketCallbackRelevant(data, state)) {
      _.assignIn(state.whiteboard, data.whiteboard)
    }
  })
  // One or multiple whiteboard canvas elements were updated by a different user
  p.$socket.on(
    'update_whiteboard_elements',
    (data: any) => {
      if ($_isSocketCallbackRelevant(data, state)) {
        const elements = data.whiteboardElements
        // Deactivate the current group if any of the updated elements are in the current group
        $_deactiveActiveGroupIfOverlap(elements)
        // Update the elements
        _.each(elements, (element: any) => {
          $_updateCanvasElement(state, element.uuid, element)
        })
        // Recalculate the size of the whiteboard canvas
        setCanvasDimensions(state)
      }
    }
  )
  // A whiteboard canvas element was added by a different user
  p.$socket.on(
    'add',
    (data: any) => {
      if ($_isSocketCallbackRelevant(data, state)) {
        _.each(data.whiteboardElements, (element: any) => {
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
      }
    }
  )
  // One or multiple whiteboard canvas elements were deleted by a different user
  p.$socket.on(
    'delete',
    (data: any) => {
      if ($_isSocketCallbackRelevant(data, state)) {
        // Deactivate the current group if any of the deleted elements are in the current group
        const elements = data.whiteboardElements
        $_deactiveActiveGroupIfOverlap(elements)
        // Delete the elements
        _.each(elements, function(element) {
          element = $_getCanvasElement(element.uuid)
          if (element) {
            p.$canvas.remove(element)
          }
        })
        // Recalculate the size of the whiteboard canvas
        setCanvasDimensions(state)
      }
    }
  )
}

const $_addViewportListeners = (state: any) => {
  // Detect keydown events in the whiteboard to respond to keyboard shortcuts
  const element = document.getElementById('whiteboard-viewport')
  if (element) {
    element.addEventListener('keydown', (event: any) => {
      if (!state.disableAll) {
        if (event.keyCode === 8 || event.keyCode === 46) {
          // Delete or backspace
          deleteActiveElements(state)
          event.preventDefault()
        } else if (event.keyCode === 67 && event.metaKey) {
          // Copy
          const activeObjects = p.$canvas.getActiveObjects()
          const clones: any[] = []
          _.each(activeObjects, (object: any, index: number) => {
            object.clone((clone: any) => {
              clones.push(clone)
              if (index === activeObjects.length - 1) {
                store.dispatch('whiteboarding/setClipboard', clones)
              }
            })
          })
        } else if (event.keyCode === 86 && event.metaKey && state.clipboard) {
          // Paste
          $_paste(state)
        }
      }
    }, false)
  }
}

const $_calculateGlobalElementPosition = (selection: any, element: any): any => {
  // Calculate the position of an element in a group relative to the whiteboard canvas.
  // This function returns the position of the element relative to the whiteboard canvas.
  // Will return the `angle`, `left` and `top` postion and the `scaleX` and `scaleY` scaling factors
  //
  // selection         The selection (group of objects) of which the element is a part
  // element           The Fabric.js element for which the position relative to its group should be calculated
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
 * Calculate the top left position of an element in a group
 *
 * selection         The selection (group of objects) of which the element is a part
 * element           The Fabric.js element for which the top left position in its group should be calculated
 * @return {Object}                           The top left position of the element in its group. Will return the `top` and `left` postion
 */
 const $_calculateRotatedLeftTop = (selection: any, element: any): any => {
  const groupAngle = selection.getAngle() * (Math.PI / 180)
  const left = (-Math.sin(groupAngle) * element.getTop() * selection.get('scaleY') + Math.cos(groupAngle) * element.getLeft() * selection.get('scaleX'))
  const top = (Math.cos(groupAngle) * element.getTop() * selection.get('scaleY') + Math.sin(groupAngle) * element.getLeft() * selection.get('scaleX'))
  return {left, top}
}

const $_deactiveActiveGroupIfOverlap = (elements: any[]) => {
  // CONCURRENT EDITING
  // Deactivate the active group if any of the provided elements are a part of the active group
  // elements: The elements that should be checked for presence in the active group
  const selection = p.$canvas.getActiveObject()
  if (selection.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
    const intersection = _.intersection(_.map(selection.objects, 'uuid'), _.map(elements, 'uuid'))
    if (intersection.length > 0) {
      p.$canvas.discardActiveGroup().requestRenderAll()
    }
  }
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
  let object = undefined
  if (element.type === 'image') {
    // In order to avoid cross-domain errors when loading images from different domains,
    // the source of the element needs to be temporarily cleared and set manually once
    // the element has been created
    element.realSrc = element.src
    element.src = ''
    fabric[type].fromObject(element, (e: any) => {
      e.setSrc(e.get('realSrc'), () => callback(e))
    })
  // TODO: Why the special treatment for 'async'?
  // } else if (fabric[type].async) {
  //   fabric[type].fromObject(element, callback)
  // } else {
  //   fabric[type].fromObject(element)
  } else {
    object = fabric[type].fromObject(element, callback)
  }
  return object
}

const $_ensureWithinCanvas = (event: any) => {
  // Ensure that the currently active object or group can not be positioned off screen
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

const $_getActiveObjects = () => {
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

const $_getCanvasElement = (uuid: string) => {
  let element = undefined
  _.each(p.$canvas.getObjects(), (e: any) => {
    if (e.get('uuid') === uuid) {
      element = e
      return false
    }
  })
  return element
}

const $_getHelperObject = () => _.find(p.$canvas.getObjects(), (o: any) => o.isHelper)

const $_getUserSession = (state: any) => {
  return {
    socketId: p.$socket.id,
    userId: p.$currentUser.id,
    whiteboardId: state.whiteboard.id
  }
}

const $_initCanvas = (state: any) => {
  // Initialize the Fabric.js canvas and load the whiteboard content and online users
  // Ensure that the horizontal and vertical origins of objects are set to center
  fabric.Object.prototype.originX = fabric.Object.prototype.originY = 'center'
  // Set the selection style for the whiteboard
  // Set the style of the multi-select helper
  p.$canvas = new fabric.Canvas('canvas', {
    selectionColor: 'transparent',
    selectionBorderColor: '#0295DE',
    selectionLineWidth: 2
  })
  $_addDebugListenters(p.$canvas, 'Canvas')
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
  p.$canvas.pencilBrush = new fabric.PencilBrush(p.$canvas)
  // Render the whiteboard
  $_addListenters(state)
  $_renderWhiteboard(state)
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
        isHelper: this.isHelper,
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
        $_saveElementUpdates([element], state)
      }
      store.dispatch('whiteboarding/setMode', 'move')
    }
  })
  // Recalculate the size of the p.$canvas when the window is resized
  window.addEventListener('resize', () => setCanvasDimensions(state))
}

const $_initSocket = (state: any, whiteboard: any) => {
  Vue.prototype.$socket = io(apiUtils.apiBaseUrl(), {
    query: {
      whiteboardId: whiteboard.id
    }
  })
  p.$socket.on('connect', () => p.$socket.emit('join', $_getUserSession(state)))
}

const $_isSocketCallbackRelevant = (data: any, state: any) => (data.socketId !== p.$socket.id && data.whiteboardId === state.whiteboard.id)

const $_paste = (state: any): void => {
  const elements: any[] = []

  // Activate the pasted element(s)
  const selectPasted = _.after(state.clipboard.length, () => {
    // When only a single element was pasted, simply select it
    if (elements.length === 1) {
      p.$canvas.setActiveObject(elements[0])
    // When multiple elements were pasted, create a new group
    // for those elements and select them
    } else {
      const selection = new fabric.ActiveSelection(elements)
      selection.isHelper = true
      $_addDebugListenters(selection, 'Object')
      p.$canvas.setActiveObject(selection)
    }
    p.$canvas.requestRenderAll()
    // Set the size of the whiteboard canvas
    setCanvasDimensions(state)
    store.dispatch('whiteboarding/setClipboard', undefined)
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
      element.clone((clone: any) => {
        delete clone.index
        delete clone.uuid
        clone.left += 25
        clone.top += 25
        // Add the element to the whiteboard canvas
        const callback = (e: any) => {
          p.$canvas.add(e)
          p.$canvas.requestRenderAll()
          // Keep track of the added elements to allow them to be selected
          elements.push(e)
          selectPasted()
        }
        $_deserializeElement(state, clone, clone.uuid, callback)
      })
    })
  }
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

const $_restoreLayers = (state: any) => {
  // Ensure that all elements are ordered as specified by the element's index attribute.
  p.$canvas.getObjects().sort((elementA: any, elementB: any) => elementA.index - elementB.index)
  p.$canvas.requestRenderAll()
  setCanvasDimensions(state)
}

const $_saveDeleteElements = (elements: any[], state: any): any => {
  // Notify the server about the deleted elements
  p.$socket.emit(
    'delete',
    {
      socketId: p.$socket.id,
      userId: p.$currentUser.id,
      whiteboardElements: _.map(elements, (element: any) => ({element})),
      whiteboardId: state.whiteboard.id
    },
    () => {
      $_updateLayers(state)
      setCanvasDimensions(state)
    }
  )
}

const $_saveElementUpdates = (elements: any[], state: any) => {
  p.$socket.emit(
    'update_whiteboard_elements',
    {
      socketId: p.$socket.id,
      userId: p.$currentUser.id,
      whiteboardElements: _.map(elements, (element: any) => ({element})),
      whiteboardId: state.whiteboard.id
    },
    () => setCanvasDimensions(state)
  )
}

const $_saveNewElement = (element: any, state: any) => {
  if (!element.uuid) {
    p.$socket.emit(
      'add',
      {
        socketId: p.$socket.id,
        userId: p.$currentUser.id,
        whiteboardElements: [{
          assetId: undefined,
          element: element.toObject()
        }],
        whiteboardId: state.whiteboard.id
      },
      (whiteboardElements: any[]) => element.uuid = whiteboardElements[0].element.uuid
    )
  }
}

const $_updateCanvasElement = (state: any, uuid: string, update: any) => {
  const element: any = $_getCanvasElement(uuid)

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

const $_updateLayers = (state: any) => {
  // Update the index of all elements to reflect their order in the current whiteboard.
  p.$canvas.forEachObject((element: any) => {
    // Only update the elements for which the stored index no longer matches the current index.
    const objects = p.$canvas.getObjects()
    const indexOf = objects.indexOf(element)
    if (element.index !== indexOf) {
      element.index = indexOf
      if (element.group) {
        // If the element is part of a group, calculate its global coordinates
        const position = $_calculateGlobalElementPosition(element.group, element)
        $_saveElementUpdates([_.assignTo({}, element.toObject(), position)], state)
      } else {
        $_saveElementUpdates([element.toObject()], state)
      }
    }
  })
}
