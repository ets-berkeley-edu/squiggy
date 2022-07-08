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
  $_log('Add asset')
  setMode('move')
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

export function afterChangeMode(state: any) {
  p.$canvas.discardActiveObject().requestRenderAll()
  p.$canvas.isDrawingMode = state.mode === 'draw'
  if (['text', 'shape'].includes(state.mode)) {
    p.$canvas.forEachObject(object => {
      object.selectable = false
      object.evented = false
    })
  } else {
    p.$canvas.forEachObject(object => {
      object.selectable = true
      object.evented = true
    })
  }
  if (state.mode === 'move') {
    $_enableCanvasElements(true)
    store.dispatch('whiteboarding/setDisableAll', false).then(_.noop)
  } else if (state.mode === 'text') {
    p.$canvas.cursor = 'text'
  }
}

export function deleteActiveElements(state: any) {
  $_log('Delete active elements')
  _.each($_getActiveObjects(), (element: any) => {
    $_broadcastDelete(element, state).then(() => p.$canvas.remove($_getCanvasElement(element.uuid)))
  })
  // If a group selection was made, remove the group as well in case Fabric doesn't clean up after itself
  const activeObject = p.$canvas.getActiveObject()
  if (activeObject && activeObject.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
    p.$canvas.remove(activeObject)
    p.$canvas.discardActiveObject().requestRenderAll()
  }
}

export function emitWhiteboardUpdate(state: any, whiteboard: any) {
  $_log('Emit whiteboard update')
  document.title = `${whiteboard.title} | SuiteC`
  state.whiteboard.title = whiteboard.title
  state.whiteboard.users = whiteboard.users
  state.whiteboard.deletedAt = whiteboard.deletedAt
  const args = {
    title: whiteboard.title,
    userId: p.$currentUser.id,
    users: whiteboard.users,
    whiteboardId: state.whiteboard.id
  }
  p.$socket.emit('update_whiteboard', args, () => {
    if (!p.$currentUser.isAdmin && !p.$currentUser.isTeaching) {
      const userIds = _.map(whiteboard.users, 'id')
      if (!_.includes(userIds, p.$currentUser.id)) {
        window.close()
      }
    }
  })
}

export function initialize(state: any) {
  $_log('Initialize')
  return new Promise<void>(resolve => {
    if (state.whiteboard.isReadOnly) {
      $_initCanvas(state)
      $_renderWhiteboard(state).then(() => {
        $_enableCanvasElements(false)
        resolve()
      })
    } else {
      $_initSocket(state)
      // Order matters: (1) set up Fabric prototypes, (2) initialize the canvas.
      $_initFabricPrototypes(state)
      $_initCanvas(state)
      $_addViewportListeners(state)
      $_renderWhiteboard(state).then(() => {
        $_addSocketListeners(state)
        $_addCanvasListeners(state)
        resolve()
      })
    }
  })
}

export function moveLayer(direction: string, state: any) {
  $_log('Move layer')
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
  $_updateLayers(state).then(() => {
    if (elements.length === 1) {
      // When only a single item was selected, re-select it
      p.$canvas.setActiveObject($_getCanvasElement(elements[0].uuid))
    }
  })
}

export function refreshPreviewImages(state: any) {
  return new Promise<void>(resolve => {
    $_log('Refresh preview images')
    const args = {
      userId: p.$currentUser.id,
      whiteboardId: state.whiteboard.id
    }
    p.$socket.emit('fetch_whiteboard', args, (data: any) => {
      if (_.get(data, 'status') === 404) {
        window.close()
        resolve()
      } else {
        store.commit('whiteboarding/setUsers', data.users)
        const whiteboardElements = data.whiteboardElements
        const count = whiteboardElements.length

        if (count) {
          let modified = false
          const after = (index) => {
            if (index === count - 1) {
              if (modified) {
                $_updateLayers(state).then(() => setCanvasDimensions(state)).then(resolve)
              } else {
                resolve()
              }
            }
          }
          _.each(whiteboardElements, (whiteboardElement: any, index: number) => {
            // We have an annotated whiteboard. Whiteboard-element objects are tagged per remote changes.
            const uuid = whiteboardElement.uuid
            $_updatePreviewImage(whiteboardElement.element.src, state, uuid).then((wasUpdated: boolean) => {
              modified = wasUpdated
              after(index)
            })
          })
        } else {
          resolve()
        }
      }
    })
  })
}

export function reload(state: any) {
  return new Promise<void>(resolve => {
    $_log('Reload')
    const isReadOnly = state.whiteboard.isReadOnly
    store.dispatch('whiteboarding/setDisableAll', isReadOnly).then(_.noop)
    if (isReadOnly) {
      $_initCanvas(state)
      $_renderWhiteboard(state).then(() => {
        $_enableCanvasElements(isReadOnly)
        resolve()
      })
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
        $_renderWhiteboard(state).then(() => {
          $_enableCanvasElements(isReadOnly)
          resolve()
        })
      }
    }
  })
}

export function setCanvasDimensions(state: any) {
  $_log('Set canvas dimensions')
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

  _.each(p.$canvas.getObjects(), (element: any) => {
    const bound = element.group ? element.group.getBoundingRect() : element.getBoundingRect()
    maxRight = Math.max(maxRight, bound.left + bound.width)
    maxBottom = Math.max(maxBottom, bound.top + bound.height)
  })

  if (maxRight > viewportWidth || maxBottom > viewportHeight) {
    store.commit('whiteboarding/setIsScrollingCanvas', true)
    // Add padding when the canvas can be scrolled
    if (maxRight > viewportWidth) {
      maxRight += constants.CANVAS_PADDING
    }
    if (maxBottom > viewportHeight) {
      maxBottom += constants.CANVAS_PADDING
    }
  } else {
    store.commit('whiteboarding/setIsScrollingCanvas', false)
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

export function setMode(mode: string) {
  $_log(`Set mode: ${mode}`)
  store.dispatch('whiteboarding/setMode', mode).then(_.noop)
}

/**
 * ---------------------------------------------------------------------------------------
 * Public functions above. Private functions below.
 * ---------------------------------------------------------------------------------------
 */

const $_addCanvasListeners = (state: any) => {
  $_log('Add canvas listeners')
  // Indicate that the currently selected elements are in the process of being moved, scaled or rotated
  p.$canvas.on('object:scaling', () => $_setModifyingElement(true))
  p.$canvas.on('object:rotating', () => $_setModifyingElement(true))
  p.$canvas.on('object:moving', (event: any) => {
    $_setModifyingElement(true)
    $_ensureWithinCanvas(event.target)
  })

  p.$canvas.on('object:modified', (event: any) => {
    $_setModifyingElement(false)
    // Ensure that none of the modified objects are positioned off-screen.
    $_ensureWithinCanvas(event.target)
    _.each($_getActiveObjects(), (element: any) => $_broadcastUpsert(element.assetId, element, state))
  })

  p.$canvas.on('after:render', () => {
    const selection = p.$canvas.getActiveObject()
    if (!_.isEmpty(selection) && !state.isModifyingElement) {
      // (1) Draw a box around the currently selected element(s), and
      // (2) position buttons that allow the selected element(s) to be modified.
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
    $_log(`canvas object:added (mode = ${state.mode})`)
    const element = event.target
    const isNonEmptyIText = element.type !== 'i-text' || element.text.trim()
    const wasAddedByRemote = state.remoteUUIDs.includes(element.uuid)
    if (isNonEmptyIText && !wasAddedByRemote && !element.isHelper) {
      $_enableCanvasElements(true)
      element.uuid = element.uuid || uuidv4()
      $_broadcastUpsert(element.assetId, element, state)
      setCanvasDimensions(state)
      setMode('move')
    }
  })

  p.$canvas.on('mouse:down', (event: any) => {
    $_log(`canvas mouse:down (mode = ${state.mode})`)
    if (state.mode === 'shape') {
      store.commit('whiteboarding/setIsDrawingShape', true)
      // Keep track of the point where drawing the shape started
      store.commit('whiteboarding/setStartShapePointer', p.$canvas.getPointer(event.e))
      // Create selected shape to use as the drawing guide. The originX and originY of the helper element are set to
      // left and top to make it easier to map the top left corner of the drawing guide with original cursor position.
      // We use 'isHelper' to indicate that the element should NOT be persisted to Squiggy db.
      const shape = new fabric[state.selected.shape]({
        fill: state.selected.fill,
        height: 10,
        index: $_getNextAvailableObjectIndex(),
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
        fontSize: state.selected.fontSize || constants.TEXT_SIZE_OPTIONS[0].value,
        height: 100,
        index: $_getNextAvailableObjectIndex(),
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
    $_log(`canvas mouse:up (mode = ${state.mode})`)
    if (state.isDrawingShape) {
      const shape = $_getHelperObject()
      store.commit('whiteboarding/setStartShapePointer', undefined)
      // Clone the drawn shape and add the clone to the canvas. This is caused by a bug in Fabric where it initially
      // uses the size when drawing started to position the controls. Cloning ensures that the controls are added in
      // the correct position. The origin of element is set to `center` to make it inline with the other elements.
      if (shape) {
        store.commit('whiteboarding/setIsDrawingShape', false)
        shape.left += shape.width / 2
        shape.top += shape.height / 2
        shape.originX = shape.originY = 'center'
        shape.isHelper = false
        // Save the added shape and make it active.
        p.$canvas.bringToFront(shape)
        $_broadcastUpsert(NaN, shape, state)
      }
      setMode('move')
    }
    $_enableCanvasElements(true)
  })

  const setActiveCanvasObject = (object: any) => store.commit('whiteboarding/setActiveCanvasObject', object)
  p.$canvas.on('selection:created', () => {
    setActiveCanvasObject(p.$canvas.getActiveObject())
    $_setModifyingElement(false)
  })
  p.$canvas.on('selection:cleared', () => setActiveCanvasObject(null))
  p.$canvas.on('selection:updated', () => setActiveCanvasObject(p.$canvas.getActiveObject()))
}

const $_addSocketListeners = (state: any) => {
  $_log('Add socket listeners')
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
    store.commit('whiteboarding/setUsers', data.users)
    $_log(`socket.on join: user_id = ${data.id}`)
  })

  p.$socket.on('leave', (data: any) => {
    store.commit('whiteboarding/setUsers', data.users)
    $_log(`socket.on leave: user_ids = ${_.map(data.users, ['id'])}`)
  })

  p.$socket.on('update_whiteboard', (data: any) => _.assignIn(state.whiteboard, data.whiteboard))

  p.$socket.on('upsert_whiteboard_element', (data: any) => {
    const whiteboardElement = data.whiteboardElement
    const element = whiteboardElement.element
    const uuid = whiteboardElement.uuid
    $_log(`socket.on upsert_whiteboard_element: type = ${element.type}, uuid = ${uuid}`)
    const existing = $_getCanvasElement(uuid)
    if (existing) {
      // Deactivate the current group if any of the updated elements are in the current group
      $_deactivateGroupIfOverlap(uuid)
      $_updatePreviewImage(element.src, state, uuid).then((modified) => {
        modified ||= $_assignIn(existing, element)
        if (modified) {
          $_ensureWithinCanvas(existing)
          setCanvasDimensions(state)
        }
      })
    } else {
      $_deserializeElement(state, element, uuid).then((e: any) => {
        // Add the element to the whiteboard canvas and move it to its appropriate index
        store.commit('whiteboarding/pushRemoteUUID', e.uuid)
        p.$canvas.add(e)
        p.$canvas.requestRenderAll()
        // Recalculate the size of the whiteboard canvas
        setCanvasDimensions(state)
      })
    }
  })

  // One or multiple whiteboard canvas elements were deleted by a different user
  p.$socket.on('delete_whiteboard_element', (data: any) => {
    const uuid = data.uuid
    const element = $_getCanvasElement(uuid)
    if (element) {
      // Deactivate the current group if any of the deleted elements are in the current group
      $_deactivateGroupIfOverlap(uuid)
      // p.$canvas.setActiveObject(element)
      p.$canvas.remove(element)
      p.$canvas.requestRenderAll()
      // Recalculate the size of the whiteboard canvas
      setCanvasDimensions(state)
    }
  })
}

const $_addViewportListeners = (state: any) => {
  $_log('Add viewport listeners')
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
          _.each(activeObjects, (object: any) => {
            object.clone((clone: any) => {
              clone.index = $_getNextAvailableObjectIndex()
              clone.uuid = uuidv4()
              clone.left += 25
              clone.top += 25
              store.commit('whiteboarding/copy', clone)
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

const $_broadcastDelete = (element: any, state: any) => {
  return new Promise<void>(resolve => {
    const args = {
      userId: p.$currentUser.id,
      whiteboardElement: {element},
      whiteboardId: state.whiteboard.id
    }
    p.$socket.emit('delete_whiteboard_element', args, resolve)
  })
}

const $_broadcastUpsert = (assetId: number, element: any, state: any) => {
  $_log('Broadcast upsert')
  const args = {
    userId: p.$currentUser.id,
    whiteboardElement: {
      assetId,
      element
    },
    whiteboardId: state.whiteboard.id
  }
  p.$socket.emit('upsert_whiteboard_element', args)
}

const $_calculateGlobalElementPosition = (selection: any, element: any): any => {
  $_log('Calculate global element position')
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

 const $_calculateRotatedLeftTop = (selection: any, element: any): any => {
  $_log('Calculate rotated left top')
  // selection: Object group of which the element is a part
  // element: Fabric element for which the top left position in its group should be calculated
  const groupAngle = selection.angle * (Math.PI / 180)
  const scaleX = selection.get('scaleX')
  const scaleY = selection.get('scaleY')
  const left = (-Math.sin(groupAngle) * element.top * scaleY + Math.cos(groupAngle) * element.left * scaleX)
  const top = (Math.cos(groupAngle) * element.top * scaleY + Math.sin(groupAngle) * element.left * scaleX)
  // Returns `top` and `left` position of the element in its group.
  return {left, top}
}

const $_deactivateGroupIfOverlap = (uuid: string) => {
  $_log('Deactivate group if overlap')
  // CONCURRENT EDITING
  // Deactivate the active group if any of the provided elements are a part of the active group
  // elements: The elements that should be checked for presence in the active group
  const selection = p.$canvas.getActiveObject()
  if (selection && selection.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
    if (_.map(selection.objects, 'uuid').includes(uuid)) {
      p.$canvas.discardActiveGroup().requestRenderAll()
    }
  }
}

const $_deserializeElement = (
  state: any,
  element: any,
  uuid: string
) => {
  return new Promise<Object>(resolve => {
    element = _.cloneDeep(element)
    element.uuid = uuid
    $_log(`Deserialize ${element.type} element (uuid: ${uuid})`)
    if (state.whiteboard.isReadOnly) {
      element.selectable = false
    }
    const type = fabric.util.string.camelize(fabric.util.string.capitalize(element.type))
    if (element.type === 'image') {
      fabric[type].fromObject(element, (e: any) => {
        const src = element.src || constants.ASSET_PLACEHOLDERS['file']
        e.setSrc(src, resolve)
      })
    } else {
      fabric[type].fromObject(element, resolve)
    }
  })
}

const $_enableCanvasElements = (enabled: boolean) => {
  $_log(`Enable canvas elements (enabled = ${enabled})`)
  p.$canvas.selection = enabled
  _.each(p.$canvas.getObjects(), (element: any) => element.selectable = enabled)
}

const $_ensureWithinCanvas = (object: any) => {
  $_log('Ensure within canvas')
  // Ensure that active object or group cannot be positioned off-screen.
  object.setCoords()
  const bound = object.getBoundingRect()
  if (bound.left < 0) {
    object.left -= bound.left / p.$canvas.getZoom()
  }
  if (bound.top < 0) {
    object.top -= bound.top / p.$canvas.getZoom()
  }
}

const $_getActiveObjects = () => {
  $_log('Get active objects')
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
  $_log('Get canvas element')
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

const $_getNextAvailableObjectIndex = () => _.max(_.map(p.$canvas.getObjects(), 'index')) + 1

const $_initCanvas = (state: any) => {
  $_log('Init canvas')
  // Ensure that the horizontal and vertical origins of objects are set to center.
  fabric.Object.prototype.originX = fabric.Object.prototype.originY = 'center'
  // Set selection style.
  const lightBlue = constants.COLORS.lightBlue.hex
  p.$canvas = new fabric.Canvas('canvas', {
    selectionColor: 'transparent',
    selectionBorderColor: lightBlue,
    selectionLineWidth: 2
  })
  if (!state.whiteboard.isReadOnly) {
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
  }
}

const $_initFabricPrototypes = (state: any) => {
  $_log('Init fabric prototypes')
  fabric.Object.prototype.toObject = (function(toObject) {
    // Extend the Fabric.js `toObject` deserialization function to include the property that
    // uniquely identifies an object on the canvas, as well as a property containing the index
    // of the object relative to the other items on the canvas.
    return function() {
      const index = _.isNil(this.index) ? $_getNextAvailableObjectIndex() : this.index
      const extras = {
        assetId: this.assetId,
        height: this.height,
        index,
        isHelper: this.isHelper,
        radius: this.radius,
        text: this.text,
        uuid: this.uuid,
        width: this.width
      }
      return fabric.util.object.extend(toObject.call(this), extras)
    }
  }(fabric.Object.prototype.toObject))

  // IMPORTANT: Do not use arrow function below. If you do then 'this' will be undefined.
  fabric.IText.prototype.on('editing:exited', function() {
    // An IText whiteboard canvas element was updated by the current user.
    const element:any = this
    if (element) {
      // If the text element is empty, it can be removed from the whiteboard canvas
      const text = element.text.trim()
      const uuid = element.get('uuid')
      if (text) {
        // The text element existed before. Notify the server that the element was updated
        const days_until_retirement = $_getDaysUntilRetirement()
        if (days_until_retirement === 0) {
          element.text = 'Sorry, SuiteC is past its expiration date. Please rebuild it, in Perl. Thank you.'
        } else if (text.toLowerCase() === 'when will teena retire?') {
          element.text = `${days_until_retirement} days until freedom`
        }
        $_broadcastUpsert(NaN, element, state)
        setMode('move')
      } else if (uuid) {
        $_broadcastDelete(element, state).then(() => {
          p.$canvas.remove(element)
          $_updateLayers(state).then(() => {
            setMode('move')
          })
        })
      } else {
        p.$canvas.remove(element)
        setMode('move')
      }
    }
  })
  // Recalculate the size of the p.$canvas when the window is resized
  window.addEventListener('resize', () => setCanvasDimensions(state))
}

const $_initSocket = (state: any) => {
  $_log('Init socket')
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
    $_log(`socket.on connect_error: ${error}`, true)
    $_tryReconnect(state)
  })
  p.$socket.on('connect_timeout', data => $_log(`[WARN] connect_timeout: ${data}`, true))
  p.$socket.on('connect', () => {
    $_log(`socket.on connect ${p.$socket.id}`)
    const engine: any = p.$socket.io.engine
    if (engine && engine.transport) {
      engine.once('upgrade', () => $_log(`socket.engine.once -> upgrade: ${engine.transport.name}`))
      engine.on('close', (reason: string) => $_log(`socket.engine.on -> close: ${reason}`))
    }
    $_join(state)
  })
}

const $_join = (state: any) => {
  $_log('Join')
  const userId: number = p.$currentUser.id
  const args = {
    userId: userId,
    whiteboardId: state.whiteboard.id
  }
  p.$socket.emit('join', args, () => store.commit('whiteboarding/join', userId))
}

const $_leave = (state: any) => {
  $_log('Leave')
  const args = {
    userId: p.$currentUser.id,
    whiteboardId: state.whiteboard.id
  }
  p.$socket.emit('leave', args, () => p.$socket.disconnect())
}

const $_log = (statement: string, force?: boolean) => {
  if (p.$config.isVueAppDebugMode || force) {
    console.log(`🪲 ${statement}`)
  }
}

const $_paste = (state: any): void => {
  $_log('Paste')
  const copies = state.clipboard
  store.commit('whiteboarding/clearClipboard')

  if (copies.length) {
    // Clear the current selection
    const object = p.$canvas.getActiveObject()
    if (object.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
      p.$canvas.remove(object)
    }
    _.each(copies, (copy: any) => p.$canvas.add(copy))
    setCanvasDimensions(state)
    _.each(copies, (copy: any) => $_ensureWithinCanvas(copy))
    if (copies.length === 1) {
      const object = $_getCanvasElement(copies[0].uuid)
      p.$canvas.setActiveObject(object).requestRenderAll()
    } else {
      // When multiple elements were pasted, create a new group for those elements and select them
      const selection = new fabric.ActiveSelection(copies)
      selection.isHelper = true
      p.$canvas.setActiveObject(selection)
      $_ensureWithinCanvas(selection)
      p.$canvas.requestRenderAll()
    }
  }
}

const $_renderWhiteboard = (state: any) => {
  return new Promise<void>(resolve => {
    $_log('Render whiteboard')
    const whiteboardElements = _.sortBy(state.whiteboard.whiteboardElements, (w: any) => `${w.element.index}-${w.element.uuid}`)
    let deserializeCount = 0
    const done = () => {
      return new Promise<void>(resolve => {
        $_updateLayers(state).then(() => {
          // Deactivate all elements and element selection when the whiteboard is being rendered in read-only mode.
          if (state.whiteboard.isReadOnly) {
            p.$canvas.discardActiveObject()
            p.$canvas.selection = false
          }
          // Render whiteboard and its elements. Set canvas size once all layout changes have been applied.
          setTimeout(() => {
            setCanvasDimensions(state)
            resolve()
          }, 0)
        })
      })
    }
    if (whiteboardElements.length) {
      _.each(whiteboardElements, (whiteboardElement: any, index: number) => {
        $_deserializeElement(
          state,
          whiteboardElement.element,
          whiteboardElement.uuid
        ).then((e: any) => {
          deserializeCount++
          p.$canvas.insertAt(e, index, false)
          // Restore the order of the layers once all elements have finished loading
          if (deserializeCount === whiteboardElements.length) {
            done().then(resolve)
          }
        })
      })
    } else {
      done().then(resolve)
    }
  })
}

const $_scaleImageObject = (element: any, state: any) => {
  $_log('Scale image object')
  // Scale the element to ensure it takes up a maximum of 80% of the visible viewport width and height
  const maxWidth = state.viewport.clientWidth * 0.8 / p.$canvas.getZoom()
  const widthRatio = maxWidth / element.width
  const maxHeight = state.viewport.clientHeight * 0.8 / p.$canvas.getZoom()
  const heightRatio = maxHeight / element.height
  // Determine which side needs the most scaling for the element to fit on the screen
  const ratio = _.min([widthRatio, heightRatio])
  if (ratio < 1) {
    $_log(`Scale image element: ratio = ${ratio}`)
    element.scale(ratio)
  }
}

const $_setModifyingElement = (value: boolean) => store.commit('whiteboarding/setIsModifyingElement', value)

const $_tryReconnect = (state: any) => {
  $_log('Try reconnect')
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

const $_assignIn = (object: any, source: any) => {
  $_log('Assign in')
  let modified = false
  _.each(constants.MUTABLE_ELEMENT_ATTRIBUTES, (key: string) => {
    const value = source[key]
    modified ||= value !== object.get(key)
    object.set(key, value)
  })
  return modified
}

const $_updatePreviewImage = (src: any, state: any, uuid: string) => {
  return new Promise<boolean>(resolve => {
    $_log('Update preview image')
    const existing: any = $_getCanvasElement(uuid)
    if (existing && (existing.type === 'image') && (existing.getSrc() !== src)) {
      // Preview image of this asset has changed. Update existing element and re-render.
      const done = (src: any) => {
        existing.setSrc(src, () => {
          $_scaleImageObject(existing, state)
          $_log(`Update existing image element: src = ${src}, uuid = ${uuid}. Next, broadcast upsert.`)
          $_renderWhiteboard(state).then(() => {
            $_ensureWithinCanvas(existing)
            resolve(true)
          })
        })
      }
      $_deactivateGroupIfOverlap(uuid)
      if (src) {
        fabric.util.loadImage(src, img => done(img.currentSrc))
      } else {
        done(existing.getSrc() || constants.ASSET_PLACEHOLDERS['file'])
      }
    } else {
      resolve(false)
    }
  })
}

const $_updateLayers = (state: any) => {
  return new Promise<void>(resolve => {
    $_log('Update layers')
    // Update the index of all elements to reflect their order in the current whiteboard.
    const objects = p.$canvas.getObjects()
    if (objects.length) {
      const after = (index: number) => {
        if (index === objects.length - 1) {
          resolve()
        }
      }
      _.each(objects, (element: any, index: number) => {
        // Only update the elements for which the stored index no longer matches the current index.
        const position = objects.indexOf(element)
        const previousIndex = element.index
        if (previousIndex !== position) {
          element.index = position
          if (element.group) {
            // If the element is part of a group, calculate its global coordinates
            const coordinates = $_calculateGlobalElementPosition(element.group, element)
            const e = _.assignIn({}, element.toObject(), coordinates)
            $_log(`Update element.group index. NEW value = ${coordinates}, OLD value = ${previousIndex}. Next, broadcast upsert.`)
            $_broadcastUpsert(e.assetId, e, state)
            after(index)
          } else {
            const e = element.toObject()
            $_log(`Update element index. NEW value = ${position}, OLD value = ${previousIndex}. Next, broadcast upsert.`)
            $_broadcastUpsert(e.assetId, e, state)
            after(index)
          }
        } else {
          after(index)
        }
      })
    } else {
      resolve()
    }
  })
}
