import _ from 'lodash'
import apiUtils from '@/api/api-utils'
import constants from '@/store/whiteboarding/constants'
import store from '@/store'
import Vue from 'vue'
import {io} from 'socket.io-client'
import {fabric} from 'fabric'
import {v4 as uuidv4} from 'uuid'

const p = Vue.prototype

export function addAsset(asset: any, state: any) {
  $_setMode('move')
  let imageUrl: any
  if (asset.imageUrl && asset.imageUrl.match(new RegExp(p.$config.s3PreviewUrlPattern))) {
    imageUrl = asset.imageUrl
  } else {
    // Default to a placeholder when the asset does not have a preview image
    const isImageFile = asset.assetType === 'file' && asset.mime.indexOf('image/') !== -1 && _.startsWith(asset.downloadUrl, 'http')
    imageUrl = isImageFile ? asset.downloadUrl : constants.ASSET_PLACEHOLDERS[asset.assetType]
  }
  fabric.Image.fromURL(imageUrl, (element: any) => {
    element.assetId = asset.id
    element.src = imageUrl
    element.uuid = uuidv4()
    const zoomLevel = p.$canvas.getZoom()
    const canvasCenter = {
      x: ((state.viewport.clientWidth / 2) + state.viewport.scrollLeft) / zoomLevel,
      y: ((state.viewport.clientHeight / 2) + state.viewport.scrollTop) / zoomLevel
    }
    $_scaleImageObject(element, state)
    element.left = canvasCenter.x
    element.top = canvasCenter.y

    p.$canvas.add(element)
    p.$canvas.setActiveObject(element)
    p.$canvas.bringToFront(element)
    $_broadcastUpsert(asset.id, element, state)
  })
}

export function deleteActiveElements(state: any) {
  const elements = $_getActiveObjects()
  _.each(elements, (element: any) => {
    p.$canvas.remove($_getCanvasElement(element.uuid))
    $_broadcastDelete(element, state)
  })
  // If a group selection was made, remove the group as well in case Fabric doesn't clean up after itself
  const activeObject = p.$canvas.getActiveObject()
  if (activeObject) {
    if (activeObject.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
      p.$canvas.remove(activeObject)
      p.$canvas.discardActiveObject().requestRenderAll()
    }
  }
}

export function emitWhiteboardUpdate(state: any, whiteboard: any) {
  document.title = `${whiteboard.title} | SuiteC`
  state.whiteboard.title = whiteboard.title
  state.whiteboard.users = whiteboard.users
  state.whiteboard.deletedAt = whiteboard.deletedAt
  p.$socket.emit('update_whiteboard', {
    title: whiteboard.title,
    userId: p.$currentUser.id,
    users: whiteboard.users,
    whiteboardId: state.whiteboard.id
  })
  if (!p.$currentUser.isAdmin && !p.$currentUser.isTeaching) {
    const userIds = _.map(whiteboard.users, 'id')
    if (!_.includes(userIds, p.$currentUser.id)) {
      window.close()
    }
  }
}

export function initialize(state: any) {
  state.viewport = document.getElementById(constants.VIEWPORT_ELEMENT_ID)
  if (state.whiteboard.isReadOnly) {
    state.disableAll = true
    $_initCanvas(state)
    $_renderWhiteboard(state)
    $_enableCanvasElements(false)
  } else {
    $_initSocket(state)
    $_addSocketListeners(state)
    // Order matters: (1) set up Fabric prototypes, (2) initialize the canvas.
    $_initFabricPrototypes(state)
    $_initCanvas(state)
    $_addViewportListeners(state)
  }
}

export function moveLayer(direction: string, state: any) {
  // Send selected element(s) to either the front or the back.
  const elements: any[] = $_getActiveObjects()
  // Sort selected elements by position such that they are in the same order when moved to back or front.
  elements.sort((elementA: any, elementB: any) => {
    return direction === 'back' ? elementB.index - elementA.index : elementA.index - elementB.index
  })
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
  // Persist the layers change.
  $_updateLayers(state)
  if (elements.length === 1) {
    // When only a single item was selected, re-select it
    p.$canvas.setActiveObject($_getCanvasElement(elements[0].uuid))
  }
}

export function checkForUpdates(state: any) {
  p.$socket.emit(
    'check_for_updates',
    {
      userId: p.$currentUser.id,
      whiteboardId: state.whiteboard.id
    },
    (data: any) => {
      if (data.status === 404) {
        window.close()
      } else {
        store.dispatch('whiteboarding/setUsers', data.users)
        _.each(data.whiteboardElements, whiteboardElement => {
          // We have an annotated whiteboard. Whiteboard-element objects are tagged per remote changes.
          const uuid = whiteboardElement.uuid
          const existing: any = $_getCanvasElement(uuid)
          if (existing && existing.src !== whiteboardElement.element.src) {
            // Deactivate the current group if any of the updated elements are in the current group
            $_deactivateGroupIfOverlap(whiteboardElement)
            $_updateCanvasElement(state, uuid, whiteboardElement.element)
            setCanvasDimensions(state)
          }
        })
        $_restoreLayers(state)
      }
    }
  )
}

export function refresh(state: any) {
  const isReadOnly = state.whiteboard.isReadOnly
  state.disableAll = isReadOnly
  if (isReadOnly) {
    $_initCanvas(state)
    $_renderWhiteboard(state)
  } else {
    if (!p.$socket) {
      $_initSocket(state)
      $_addSocketListeners(state)
    }
    if (!p.$canvas) {
      // Order matters: (1) set up Fabric prototypes, (2) initialize the canvas.
      $_initFabricPrototypes(state)
      $_initCanvas(state)
      $_addViewportListeners(state)
    }
  }
  $_enableCanvasElements(isReadOnly)
}

export function setCanvasDimensions(state: any) {
  // Set the width and height of the whiteboard canvas. The width of the visible canvas will be the same for all users,
  // and the canvas will be zoomed to accommodate that width. By default, the size of the zoomed canvas will be the
  // same as the size of the viewport. When there are any elements on the canvas that are outside the viewport
  // boundaries, the canvas will be enlarged to incorporate those.

  // Zoom the canvas to accommodate the base width within the viewport.
  const viewportWidth = state.viewport.clientWidth
  const ratio = viewportWidth / constants.CANVAS_BASE_WIDTH
  p.$canvas.setZoom(ratio)

  // Calculate the position of the elements that are the most right and the most bottom. When all elements fit within
  // the viewport, the canvas is made the same size as the viewport. When any elements overflow the viewport, the
  // canvas is enlarged to incorporate all assets outside the viewport
  const viewportHeight = state.viewport.clientHeight
  let maxRight = viewportWidth
  let maxBottom = viewportHeight

  p.$canvas.forEachObject((element: any) => {
    let bound
    if (!element.group) {
      bound = element.getBoundingRect()
    } else {
      bound = element.group.getBoundingRect()
    }
    maxRight = Math.max(maxRight, _.get(bound, 'left') + _.get(bound, 'width'))
    maxBottom = Math.max(maxBottom, _.get(bound, 'top') + _.get(bound, 'height'))
  })
  // Keep track of whether the canvas can currently be scrolled.
  if (maxRight > viewportWidth || maxBottom > viewportHeight) {
    store.dispatch('whiteboarding/setIsScrollingCanvas', true).then(_.noop)

    // Add padding when the canvas can be scrolled
    if (maxRight > viewportWidth) {
      maxRight += constants.CANVAS_PADDING
    }
    if (maxBottom > viewportHeight) {
      maxBottom += constants.CANVAS_PADDING
    }
  } else {
    store.dispatch('whiteboarding/setIsScrollingCanvas', false).then(_.noop)
  }
  // When the entire whiteboard content should fit within the screen, adjust the zoom level to make it fit.
  if (state.fitToScreen) {
    // Calculate the actual un-zoomed width of the whiteboard.
    const realWidth = maxRight / p.$canvas.getZoom()
    const realHeight = maxBottom / p.$canvas.getZoom()
    // Zoom the canvas based on whether the height or width needs the largest zoom out.
    const widthRatio = viewportWidth / realWidth
    const heightRatio = viewportHeight / realHeight
    const ratio = Math.min(widthRatio, heightRatio)
    p.$canvas.setZoom(ratio)

    p.$canvas.setHeight(viewportHeight)
    p.$canvas.setWidth(viewportWidth)
  } else {
    // Adjust the value for rounding issues to prevent scrollbars from incorrectly showing up.
    p.$canvas.setHeight(maxBottom - 1)
    p.$canvas.setWidth(maxRight - 1)
  }
}

export function setMode(state: any, mode: string) {
  p.$canvas.discardActiveObject().requestRenderAll()
  p.$canvas.isDrawingMode = false
  if (mode === 'move') {
    $_enableCanvasElements(true)
    state.disableAll = false
  } else if (mode === 'draw') {
    p.$canvas.isDrawingMode = true
  } else if (mode === 'text') {
    p.$canvas.cursor = 'text'
  }
  state.mode = mode
}

/**
 * ---------------------------------------------------------------------------------------
 * Public functions above. Private functions below.
 * ---------------------------------------------------------------------------------------
 */

const $_addListeners = (state: any) => {
  // Indicate that the currently selected elements are in the process of being moved, scaled or rotated
  const setModifyingElement = () => store.dispatch('whiteboarding/setIsModifyingElement', true)
  p.$canvas.on('object:moving', setModifyingElement)
  p.$canvas.on('object:scaling', setModifyingElement)
  p.$canvas.on('object:rotating', setModifyingElement)
  p.$canvas.on('object:moving', (event: any) => $_ensureWithinCanvas(event))

  // One or multiple whiteboard canvas elements have been updated by the current user
  p.$canvas.on('object:modified', (event: any) => {
    // Ensure that none of the modified objects are positioned off-screen.
    $_ensureWithinCanvas(event)
    _.each($_getActiveObjects(), (element: any) => $_broadcastUpsert(element.assetId, element, state))
  })
  // Indicate that the currently selected elements are no longer being modified once moving, scaling or rotating has finished
  p.$canvas.on('object:modified', () => store.dispatch('whiteboarding/setIsModifyingElement', false))

  // (1) Draw a box around the currently selected element(s), and
  // (2) position buttons that allow the selected element(s) to be modified.
  p.$canvas.on('after:render', () => {
    const selection = p.$canvas.getActiveObject()
    if (!_.isEmpty(selection) && !state.isModifyingElement) {
      // Get the bounding rectangle around the currently selected element(s)
      const bound = selection.getBoundingRect()
      if (bound) {
        // Explicitly draw the bounding rectangle
        p.$canvas.contextContainer.strokeStyle = constants.COLORS.lightBlue.hex
        p.$canvas.contextContainer.strokeRect(
          bound.left - 10,
          bound.top - 10,
          bound.width + 20,
          bound.height + 20
        )
      }
      // Position the buttons to modify the selected element(s)
      const editButtons = document.getElementById(constants.WHITEBOARD_ELEMENT_EDIT_ID)
      if (editButtons) {
        editButtons.style.left = (bound.left - 10) + 'px'
        editButtons.style.top = (bound.top + bound.height + 75) + 'px'
      }
    }
  })

  p.$canvas.on('before:selection:cleared', () => {
    // When a group is programmatically added then it must be programmatically removed when the group is deselected.
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

    if (!isIncompleteIText && !element.isHelper) {
      element.uuid = element.uuid || uuidv4()
      $_broadcastUpsert(element.assetId, element, state)
      setCanvasDimensions(state)
      $_setMode('move')
    }
  })

  p.$canvas.on('mouse:down', (event: any) => {
    if (state.mode === 'shape') {
      store.dispatch('whiteboarding/setIsDrawingShape', true).then(_.noop)
      // Keep track of the point where drawing the shape started
      store.dispatch('whiteboarding/setStartShapePointer', p.$canvas.getPointer(event.e)).then(_.noop)

      // Create selected shape to use as the drawing guide. The originX and originY of the helper element are set to
      // left and top to make it easier to map the top left corner of the drawing guide with original cursor position.
      // We use 'isHelper' to indicate that the element should NOT be persisted to Squiggy db.
      const shape = new fabric[state.selected.shape]({
        fill: state.selected.fill,
        height: 10,
        isHelper: true,
        left: state.startShapePointer.x,
        originX: 'left',
        originY: 'top',
        radius: 1,
        stroke: state.selected.color,
        strokeWidth: state.selected.strokeWidth,
        top: state.startShapePointer.y,
        uuid: uuidv4(),
        width: 10
      })
      p.$canvas.add(shape)
    }
    if (state.mode === 'text') {
      const textPointer = p.$canvas.getPointer(event.e)
      const iText = new fabric.IText('', {
        fill: state.selected.fill,
        fontFamily: '"HelveticaNeue-Light", "Helvetica Neue Light", "Helvetica Neue", Helvetica, Arial, "Lucida Grande", sans-serif',
        fontSize: state.selected.fontSize || 14,
        height: 100,
        left: textPointer.x,
        text: '',
        selectable: true,
        selected: true,
        top: textPointer.y,
        uuid: uuidv4()
      })
      p.$canvas.add(iText)

      // Put the editable text field in edit mode straight away
      setTimeout(function() {
        p.$canvas.setActiveObject(iText)
        iText.enterEditing()
        // The textarea needs to be put in edit mode manually.
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

      // When the user has moved the cursor to the left of the original starting point,
      // move the left of the circle to that point so negative shape drawing can be achieved
      if (state.startShapePointer.x > currentShapePointer.x) {
        shape.set({left: currentShapePointer.x})
      }
      // When the user has moved the cursor above the original starting point,
      // move the left of the circle to that point so negative shape drawing can be achieved
      if (state.startShapePointer.y > currentShapePointer.y) {
        shape.set({top: currentShapePointer.y})
      }
      // Set the radius and width of the circle based on how much the cursor has moved compared to the starting point.
      const horizontal = Math.abs(state.startShapePointer.x - currentShapePointer.x)
      const vertical = Math.abs(state.startShapePointer.y - currentShapePointer.y)
      if (_.lowerCase(state.selected.shape) === 'circle') {
        shape.set({
          height: horizontal,
          radius: Math.floor(horizontal / 2),
          width: horizontal
        })
      // Set the width and height of the shape based on how much the cursor has moved compared to the starting point.
      } else {
        shape.set({height: vertical, width: horizontal})
      }
      p.$canvas.requestRenderAll()
    }
  })

  p.$canvas.on('mouse:up', () => {
    if (state.isDrawingShape) {
      const shape = $_getHelperObject()
      // Indicate that shape drawing has stopped
      store.dispatch('whiteboarding/setIsDrawingShape', false).then(_.noop)
      $_setMode('move')
      // Clone the drawn shape and add the clone to the canvas. This is caused by a bug in Fabric where it initially
      // uses the size when drawing started to position the controls. Cloning ensures that the controls are added in
      // the correct position. The origin of element is set to `center` to make it inline with the other elements.
      if (shape) {
        shape.left += shape.width / 2
        shape.top += shape.height / 2
        shape.originX = shape.originY = 'center'
        shape.isHelper = false
        // Save the added shape and make it active.
        $_broadcastUpsert(NaN, shape, state)
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
    if (p.$socket) {
      $_leave(state)
      p.$socket.close()
    }
    if (event) {
      event.preventDefault()
    }
  }
  window.onbeforeunload = onWindowClose
  window.onunload = onWindowClose

  p.$socket.on('error', (error: any) => {
    $_log(`socket-io error: ${error}`, true)
    if (p.$socket.disconnected) {
      $_tryReconnect(state)
    }
  })
  p.$socket.on('ping', () => $_log('socket-io ping'))
  p.$socket.on('reconnect', (attempt: number) => $_log(`reconnect attempt ${attempt}`))
  p.$socket.on('reconnect_attempt', (attempt: number) => $_log(`reconnect_attempt ${attempt}`))
  p.$socket.on('reconnect_error', (error: any) => $_log(`socket-io reconnect_error: ${error}`, true))
  p.$socket.on('reconnect_failed', (error: any) => {
    $_log(`socket-io reconnect_failed: ${error}`, true)
    if (p.$socket.disconnected) {
      $_tryReconnect(state)
    }
  })

  p.$socket.on('join', (data: any) => {
    $_log(`socket-io join: ${data}`)
    store.dispatch('whiteboarding/setUsers', data.users)
  })
  p.$socket.on('leave', (data: any) => {
    $_log(`socket-io leave: ${data}`)
    store.dispatch('whiteboarding/setUsers', data.users)
  })
  p.$socket.on('update_whiteboard', (data: any) => {
    $_log(`socket-io update_whiteboard: ${data}`)
    _.assignIn(state.whiteboard, data.whiteboard)
  })
  // One or multiple whiteboard canvas elements were updated by a different user
  p.$socket.on('upsert_whiteboard_element', (data: any) => {
    $_log(`socket-io upsert_whiteboard_element: ${data}`)
    const whiteboardElement = data.whiteboardElement
    const element = whiteboardElement.element
    const uuid = whiteboardElement.uuid
    const existing = $_getCanvasElement(uuid)
    if (existing) {
      // Deactivate the current group if any of the updated elements are in the current group
      $_deactivateGroupIfOverlap(whiteboardElement)
      $_updateCanvasElement(state, whiteboardElement.uuid, element)
      setCanvasDimensions(state)
    } else {
      const callback = (e: any) => {
        // Add the element to the whiteboard canvas and move it to its appropriate index
        p.$canvas.add(e)
        p.$canvas.requestRenderAll()
        // Recalculate the size of the whiteboard canvas
        setCanvasDimensions(state)
      }
      $_deserializeElement(state, element, element.uuid, callback)
    }
  })
  // One or multiple whiteboard canvas elements were deleted by a different user
  p.$socket.on(
    'delete_whiteboard_element',
    (data: any) => {
      $_log(`socket-io delete_whiteboard_element: ${data}`)
      const element = $_getCanvasElement(data.uuid)
      if (element) {
        // Deactivate the current group if any of the deleted elements are in the current group
        $_deactivateGroupIfOverlap(element)
        // p.$canvas.setActiveObject(element)
        p.$canvas.remove(element)
        p.$canvas.requestRenderAll()
        // Recalculate the size of the whiteboard canvas
        setCanvasDimensions(state)
      }
    })
}

const $_addViewportListeners = (state: any) => {
  // Detect keydown events in the whiteboard to respond to keyboard shortcuts
  const element = document.getElementById(constants.VIEWPORT_ELEMENT_ID)
  if (element) {
    const onKeydown = (event: any) => {
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
                store.dispatch('whiteboarding/setClipboard', clones).then(_.noop)
              }
            })
          })
        } else if (event.keyCode === 86 && event.metaKey && state.clipboard) {
          // Paste
          $_paste(state)
        }
      }
    }
    element.addEventListener('keydown', onKeydown, false)
  }
}

const $_broadcastDelete = (element: any, state: any): any => {
  p.$socket.emit(
    'delete_whiteboard_element',
    {
      userId: p.$currentUser.id,
      whiteboardElement: {element},
      whiteboardId: state.whiteboard.id
    },
    () => {
      $_updateLayers(state)
      setCanvasDimensions(state)
    }
  )
}

const $_broadcastUpsert = (assetId: number, element: any, state: any) => {
  p.$socket.emit(
    'upsert_whiteboard_element',
    {
      userId: p.$currentUser.id,
      whiteboardElement: {
        assetId,
        element
      },
      whiteboardId: state.whiteboard.id
    },
    () => setCanvasDimensions(state)
  )
}

const $_calculateGlobalElementPosition = (selection: any, element: any): any => {
  // Calculate the position of an element in a group relative to the whiteboard canvas. This function returns the
  // position of the element relative to the whiteboard canvas: `angle`, `left` and `top` position and
  // the `scaleX` and `scaleY` scaling factors
  //
  // selection         The selection (group of objects) of which the element is a part
  // element           The Fabric.js element for which the position relative to its group should be calculated
  const center = selection.getCenterPoint()
  const rotated = $_calculateRotatedLeftTop(selection, element)
  return {
    angle: element.angle + selection.angle,
    left: center.x + rotated.left,
    scaleX: element.get('scaleX') * selection.get('scaleX'),
    scaleY: element.get('scaleY') * selection.get('scaleY'),
    top: center.y + rotated.top
  }
}

/**
 * selection: Object group of which the element is a part
 * element: Fabric element for which the top left position in its group should be calculated
 * Returns `top` and `left` position of the element in its group.
 */
 const $_calculateRotatedLeftTop = (selection: any, element: any): any => {
  const groupAngle = selection.angle * (Math.PI / 180)
  const scaleX = selection.get('scaleX')
  const scaleY = selection.get('scaleY')
  const left = (-Math.sin(groupAngle) * element.top * scaleY + Math.cos(groupAngle) * element.left * scaleX)
  const top = (Math.cos(groupAngle) * element.top * scaleY + Math.sin(groupAngle) * element.left * scaleX)
  return {left, top}
}

const $_deactivateGroupIfOverlap = (element: any) => {
  // CONCURRENT EDITING
  // Deactivate the active group if any of the provided elements are a part of the active group
  // elements: The elements that should be checked for presence in the active group
  const selection = p.$canvas.getActiveObject()
  if (selection && selection.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
    const intersection = _.intersection(_.map(selection.objects, 'uuid'), [element.uuid])
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
  element = _.cloneDeep(element)
  element.uuid = uuid
  if (state.whiteboard.isReadOnly) {
    element.selectable = false
  }
  const type = fabric.util.string.camelize(fabric.util.string.capitalize(element.type))
  if (element.type === 'image') {
    fabric[type].fromObject(element, (e: any) => {
      e.setSrc(element.src || constants.ASSET_PLACEHOLDERS['file'], (e: any) => {
        $_scaleImageObject(e, state)
        callback(e)
      })
    })
  } else {
    fabric[type].fromObject(element, callback)
  }
}

const $_enableCanvasElements = (enabled: boolean) => {
  p.$canvas.selection = enabled
  _.each(p.$canvas.getObjects(), (element: any) => element.selectable = enabled)
}

const $_ensureWithinCanvas = (event: any) => {
  // Ensure that active object or group cannot be positioned off-screen.
  const element = event.target
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
  const activeElements: any[] = []
  const selection = p.$canvas.getActiveObject()
  if (selection) {
    if (selection.getObjects) {
      _.each(selection.getObjects(), (element: any) => {
        // When a Fabric.js canvas is part of a group selection, its properties will be relative to the group.
        // Therefore, we calculate the actual position of each element in the group relative to the whiteboard canvas.
        const position = $_calculateGlobalElementPosition(selection, element)
        activeElements.push(_.assignIn({}, element.toObject(), position))
      })
    } else {
      activeElements.push(selection.toObject())
    }
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

const $_getDaysUntilRetirement = () => {
  const now = new Date()
  const freedom = new Date('09/12/2024')
  const diff = freedom.getTime() - now.getTime()
  return Math.floor(diff / (1000 * 3600 * 24))
}

const $_getHelperObject = () => _.find(p.$canvas.getObjects(), (o: any) => o.isHelper)

const $_initCanvas = (state: any) => {
  // Ensure that the horizontal and vertical origins of objects are set to center.
  fabric.Object.prototype.originX = fabric.Object.prototype.originY = 'center'
  // Set selection style.
  const lightBlue = constants.COLORS.lightBlue.hex
  p.$canvas = new fabric.Canvas('canvas', {
    selectionColor: 'transparent',
    selectionBorderColor: lightBlue,
    selectionLineWidth: 2
  })
  if (state.whiteboard.isReadOnly) {
    $_renderWhiteboard(state)
  } else {
    // Make the border dashed.
    p.$canvas.selectionDashArray = [10, 5]
    fabric.Object.prototype.borderColor = lightBlue
    fabric.Object.prototype.borderScaleFactor = 0.3
    fabric.Object.prototype.cornerColor = lightBlue
    fabric.Object.prototype.cornerSize = 10
    fabric.Object.prototype.transparentCorners = false
    fabric.Object.prototype.rotatingPointOffset = 30
    // Set the pencil brush as the drawing brush
    p.$canvas.pencilBrush = new fabric.PencilBrush(p.$canvas)
    $_renderWhiteboard(state)
    $_addListeners(state)
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
        isHelper: this.isHelper,
        radius: this.radius,
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
          $_broadcastDelete(element, state)
        }
        p.$canvas.remove(element)
      } else {
        // The text element existed before. Notify the server that the element was updated
        const days_until_retirement = $_getDaysUntilRetirement()
        if (days_until_retirement === 0) {
          element.text = 'Sorry, SuiteC is past its expiration date. Please rebuild it, in Perl. Thank you.'
        } else if (text.toLowerCase() === 'when will teena retire?') {
          element.text = `${days_until_retirement} days until freedom`
        }
        $_broadcastUpsert(NaN, element, state)
      }
      $_setMode('move')
    }
  })
  // Recalculate the size of the p.$canvas when the window is resized
  window.addEventListener('resize', () => setCanvasDimensions(state))
}

const $_initSocket = (state: any) => {
  const baseUrl = _.replace(_.trim(apiUtils.apiBaseUrl()), /^http/, 'ws')
  p.$socket = io(baseUrl, {
    forceNew: true,
    query: {
      whiteboardId: state.whiteboard.id
    },
    secure: true,
    transports: ['websocket', 'polling'],
    withCredentials: true
  })
  p.$socket.on('close', $_tryReconnect)
  p.$socket.on('connect_error', (error: any) => {
    $_log(`socket-io connect_error: ${error}`, true)
    $_tryReconnect(state)
  })
  p.$socket.on('connect_timeout', data => $_log(`[WARN] connect_timeout: ${data}`, true))
  p.$socket.on('connect', () => {
    $_log(`socket-io connect ${p.$socket.id}`)
    const engine: any = p.$socket.io.engine
    if (engine && engine.transport) {
      engine.once('upgrade', () => $_log(`socket-io.engine upgrade: ${engine.transport.name}`))
      engine.on('close', (reason: string) => $_log(`socket-io.engine close: ${reason}`))
    }
    $_join(state)
  })
}

const $_join = (state: any) => {
  const userId: number = p.$currentUser.id
  p.$socket.emit('join', {
    userId: userId,
    whiteboardId: state.whiteboard.id
  })
  store.dispatch('whiteboarding/join', userId).then(_.noop)
}

const $_leave = (state: any) => {
  p.$socket.emit('leave', {
    userId: p.$currentUser.id,
    whiteboardId: state.whiteboard.id
  })
  p.$socket.disconnect()
}

const $_log = (statement: string, force?: boolean) => {
  if (p.$config.isVueAppDebugMode || force) {
    console.log(statement)
  }
}

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
      p.$canvas.setActiveObject(selection)
    }
    p.$canvas.requestRenderAll()
    // Set the size of the whiteboard canvas
    setCanvasDimensions(state)
    store.dispatch('whiteboarding/setClipboard', undefined).then(_.noop)
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
        clone.uuid = uuidv4()
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
  // Render whiteboard and its elements. Set canvas size once all layout changes have been applied.
  setTimeout(() => setCanvasDimensions(state), 0)

  // Restore the order of the layers once all elements have finished loading
  const restore = _.after(state.whiteboard.whiteboardElements.length, () => {
    $_restoreLayers(state)
    // Deactivate all elements and element selection when the whiteboard
    // is being rendered in read only mode
    if (state.whiteboard.isReadOnly) {
      p.$canvas.discardActiveObject()
      p.$canvas.selection = false
    }
  })
  // Restore the layout of the whiteboard canvas
  const whiteboardElements = _.sortBy(state.whiteboard.whiteboardElements, 'element.index')
  _.each(whiteboardElements, (whiteboardElement: any) => {
    $_deserializeElement(
      state,
      whiteboardElement.element,
      whiteboardElement.uuid,
      (e: any) => {
        p.$canvas.add(e)
        restore()
      }
    )
  })
}

const $_restoreLayers = (state: any) => {
  // Ensure that all elements are ordered as specified by the element's index attribute.
  _.each(p.$canvas.getObjects(), (object: any) => {
    p.$canvas.moveTo(object, object.index)
  })
  p.$canvas.requestRenderAll()
  setCanvasDimensions(state)
}

const $_scaleImageObject = (element: any, state: any) => {
  // Scale the element to ensure it takes up a maximum of 80% of the visible viewport width and height
  const maxWidth = state.viewport.clientWidth * 0.8 / p.$canvas.getZoom()
  const widthRatio = maxWidth / element.width
  const maxHeight = state.viewport.clientHeight * 0.8 / p.$canvas.getZoom()
  const heightRatio = maxHeight / element.height
  // Determine which side needs the most scaling for the element to fit on the screen
  const ratio = _.min([widthRatio, heightRatio])
  if (ratio < 1) {
    element.scale(ratio)
  }
}

const $_setMode = (mode: string, callback?: any) => {
  store.dispatch('whiteboarding/setMode', mode).then(callback || _.noop)
}

const $_tryReconnect = (state: any) => {
  setTimeout(() => {
    $_leave(state)
    p.$socket.io.open((error: any) => {
      if (error) {
        $_log(`socket-io.open error: ${error}`, true)
        $_tryReconnect(state)
      } else {
        $_join(state)
      }
    })
  }, 2000)
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
  const objects = p.$canvas.getObjects()
  _.each(objects, (element: any) => {
    // Only update the elements for which the stored index no longer matches the current index.
    const indexOf = objects.indexOf(element)
    if (element.index !== indexOf) {
      element.index = indexOf
      if (element.group) {
        // If the element is part of a group, calculate its global coordinates
        const position = $_calculateGlobalElementPosition(element.group, element)
        const e = _.assignIn({}, element.toObject(), position)
        $_broadcastUpsert(e.assetId, e, state)
      } else {
        const e = element.toObject()
        $_broadcastUpsert(e.assetId, e, state)
      }
    }
  })
}
