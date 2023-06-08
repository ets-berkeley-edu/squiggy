import _ from 'lodash'
import apiUtils from '@/api/api-utils'
import constants from '@/store/whiteboarding/constants'
import store from '@/store'
import Vue from 'vue'
import {io} from 'socket.io-client'
import {fabric} from 'fabric'
import {v4 as uuidv4} from 'uuid'
import {deleteWhiteboardElement, updateWhiteboardElementsOrder, upsertWhiteboardElements} from '@/api/whiteboard-elements'

const p = Vue.prototype

export function addAssets(assets: any[], state: any) {
  return new Promise<void>(resolve => {
    $_log(`Add ${assets.length} assets`)
    setMode('move')
    const elements: any[] = []
    _.each(assets, asset => {
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
        elements.push(element)

        p.$canvas.add(element)
        p.$canvas.bringToFront(element)
        if (elements.length === assets.length) {
          p.$canvas.setActiveObject(element)
          $_broadcastUpsert($_translateIntoWhiteboardElements(elements), state).then(resolve)
        }
      })
    })
  })
}

export function afterChangeMode(state: any) {
  p.$canvas.discardActiveObject().requestRenderAll()
  p.$canvas.isDrawingMode = state.mode === 'draw'
  if (state.disableAll) {
    $_enableCanvasElements(false)
  } else {
    const selectable = !['text', 'shape'].includes(state.mode)
    p.$canvas.forEachObject(object => {
      object.selectable = selectable
      object.evented = selectable
    })
    if (state.mode === 'move') {
      $_enableCanvasElements(true)
      store.dispatch('whiteboarding/setDisableAll', false).then(_.noop)
    } else if (state.mode === 'text') {
      p.$canvas.cursor = 'text'
    }
  }
}

export function deleteActiveElements(state: any) {
  $_log('Delete active elements')
  const uuids: any[] = []
  _.each(getActiveObjects(), (element: any) => {
    const uuid = element.uuid
    p.$canvas.remove($_getCanvasElement(uuid))
    uuids.push(uuid)
  })
  // If a group selection was made, remove the group as well in case Fabric doesn't clean up after itself
  const activeObject = p.$canvas.getActiveObject()
  if (activeObject && activeObject.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
    p.$canvas.remove(activeObject)
    p.$canvas.discardActiveObject().requestRenderAll()
  }
  return $_broadcastDelete(uuids, state)
}

export function getActiveObjects() {
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

export function initialize(state: any) {
  $_log('Initialize')
  store.commit('whiteboarding/setIsInitialized', false)
  return new Promise<void>(resolve => {
    const done = () => {
      $_addCanvasPanningListeners(state)
      // Recalculate the size of the p.$canvas when the window is resized
      window.addEventListener('resize', () => setCanvasDimensions(state))
      store.commit('whiteboarding/setIsInitialized', true)
      resolve()
    }
    if (state.disableAll) {
      // The /asset page uses this code to render assets of type 'whiteboard'.
      // No need for socket.io connection.
      const isAsset = state.whiteboard.assetType
      if (!isAsset) {
        $_initSocket(state)
      }
      $_initCanvas(state)
      $_renderWhiteboard(state, true).then(() => {
        $_enableCanvasElements(false)
        done()
      })
    } else {
      $_initSocket(state)
      // Order matters: (1) set up Fabric prototypes, (2) initialize the canvas.
      $_initFabricPrototypes(state)
      $_initCanvas(state)
      $_addViewportListeners(state)
      $_renderWhiteboard(state, true).then(() => {
        $_addSocketListeners(state)
        $_addCanvasListeners(state)
        done()
      })
    }
  })
}

export function changeZOrder(direction: string, objects: any[], state: any) {
  $_log('Change z-order')
  const uuids: string[] = []
  _.each(objects, (e: any) => {
    if (e.type !== constants.FABRIC_MULTIPLE_SELECT_TYPE) {
      const uuid: string = e.uuid
      const element:any = $_getCanvasElement(uuid)
      if (element) {
        uuids.push(uuid)
        if (direction === 'bringToFront') {
          p.$canvas.bringToFront(element)
        } else if (direction === 'sendToBack') {
          p.$canvas.sendToBack(element)
        }
      }
    }
  })
  const apiCall = () => updateWhiteboardElementsOrder(
      direction,
      p.$socket.id,
      uuids,
      state.whiteboard.id
  )
  $_invokeWithSocketConnectRetry('update whiteboard elements order', apiCall, state)
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
  // the viewport, the canvas is made the same size as the viewport minus the toolbar. When any elements overflow the
  // viewport, the canvas is enlarged to incorporate all assets outside the viewport
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

  // Calculate the actual un-zoomed width of the whiteboard.
  const realWidth = maxRight / p.$canvas.getZoom()
  const realHeight = maxBottom / p.$canvas.getZoom()
  const maximumSize = 4000

  // When the entire whiteboard content should fit within the screen, adjust the zoom level to make it fit.

  if (state.isFitToScreen) {
    // Zoom the canvas based on whether the height or width needs the largest zoom out.
    const widthRatio = viewportWidth / realWidth
    const heightRatio = viewportHeight / realHeight
    const ratio = Math.min(widthRatio, heightRatio)
    p.$canvas.setZoom(ratio)
    p.$canvas.setHeight(viewportHeight)
    p.$canvas.setWidth(viewportWidth)

  // If the actual-size whiteboard is too big for sane display, set up a partial zoom.
  } else if (realWidth > maximumSize || realHeight > maximumSize) {

    const maxDimension = Math.max(realWidth, realHeight)
    const ratio = maximumSize / maxDimension
    const displayHeight = realHeight * ratio
    const displayWidth = realWidth * ratio

    p.$canvas.setZoom(ratio)
    p.$canvas.setHeight(displayHeight - 1)
    p.$canvas.setWidth(displayWidth - 1)

  // Otherwise display actual size, adjusting for rounding issues to prevent scrollbars from incorrectly showing up.
  } else {
    p.$canvas.setHeight(maxBottom - 1)
    p.$canvas.setWidth(maxRight - 1)
  }
}

export function setMode(mode: string) {
  $_log(`Set mode: ${mode}`)
  store.dispatch('whiteboarding/setMode', mode).then(_.noop)
}

export function updatePreviewImage(element: any, state: any, uuid: string) {
  return new Promise<boolean>(resolve => {
    const existing: any = $_getCanvasElement(uuid)
    const src = element.src
    if (existing && (existing.type === 'image') && (existing.getSrc() !== src)) {
      $_log(`Update preview image:  \nexisting:  \n${JSON.stringify(existing)}  \n----\nelement:  \n${JSON.stringify(element)}`)
      // Preview image of this asset has changed. Update existing element and re-render.
      const done = (src: any) => {
        existing.setSrc(src, () => {
          $_scaleImageObject(existing, state)
          $_renderWhiteboard(state).then(() => {
            $_ensureWithinCanvas(existing)
            p.$canvas.requestRenderAll()
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

export function zoom(delta: number) {
  $_zoom(delta)
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

  p.$canvas.on('object:modified', () => {
    $_setModifyingElement(false)
    const objects: any[] = []
    const object = p.$canvas.getActiveObject()
    if (object) {
      if (object.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
        _.each(object.getObjects(), (element: any) => {
          const position = $_calculateGlobalElementPosition(object, element)
          objects.push(_.assignIn({}, element.toObject(), position))
        })
      } else {
        objects.push(object.toObject())
      }
      if (_.size(objects)) {
        const whiteboardElements = _.map(objects, o => {
          return {assetId: o.assetId, element: o, uuid: o.uuid}
        })
        changeZOrder('bringToFront', objects, state)
        $_broadcastUpsert(whiteboardElements, state).then(() => {
          _.each(p.$canvas.getObjects(), $_ensureWithinCanvas)
          store.dispatch('whiteboarding/setIsFitToScreen', true).then(_.noop)
        })
      }
    }
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
    if (selection && selection.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
      p.$canvas.remove(selection)
    }
  })
  // Recalculate the size of the whiteboard canvas when a selection has been deselected
  p.$canvas.on('selection:cleared', () => setCanvasDimensions(state))

  p.$canvas.on('object:added', (event: any) => {
    $_log(`canvas object:added (mode = ${state.mode})`)
    const element = event.target
    const isNonEmptyIText = !['i-text','textbox'].includes(element.type) || element.text.trim()
    const wasAddedByRemote = state.remoteUUIDs.includes(element.uuid)
    if (!wasAddedByRemote && isNonEmptyIText && !element.assetId && !element.uuid && !element.isHelper) {
      $_enableCanvasElements(true)
      element.uuid = uuidv4()
      const whiteboardElements = $_translateIntoWhiteboardElements([element])
      $_broadcastUpsert(whiteboardElements, state).then(() => setCanvasDimensions(state))
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
        isHelper: true,
        left: state.startShapePointer.x,
        originX: 'left',
        originY: 'top',
        radius: 1,
        stroke: state.selected.color,
        strokeWidth: state.selected.strokeWidth,
        top: state.startShapePointer.y,
        width: 10
      })
      p.$canvas.add(shape)
    }
    if (state.mode === 'text') {
      const textPointer = p.$canvas.getPointer(event.e)
      const iText = new fabric.Textbox('', {
        fill: state.selected.fill,
        fontFamily: 'Helvetica',
        fontSize: state.selected.fontSize || constants.TEXT_SIZE_OPTIONS[0].value,
        left: textPointer.x,
        text: '',
        selectable: true,
        selected: true,
        top: textPointer.y,
        originX: 'left',
        originY: 'top',
        width: 400,
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
        shape.uuid = shape.uuid || uuidv4()
        shape.left += shape.width / 2
        shape.top += shape.height / 2
        shape.originX = shape.originY = 'center'
        shape.isHelper = false
        // Shapes are special: When a shape is added we keep it selected and set mode to 'move'
        // so it can be quickly manipulated without creating more shape objects.
        // In the case of other canvas object types, after they are added to the canvas
        // we do NOT reset the mode. We hope these varying rules are intuitive to the user.
        p.$canvas.bringToFront(shape)
        setMode('move')
        p.$canvas.setActiveObject(shape)
        const whiteboardElements = $_translateIntoWhiteboardElements([shape])
        $_broadcastUpsert(whiteboardElements, state).then(_.noop)
      }
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

const $_addCanvasPanningListeners = (state: any) => {
  p.$canvas.on('mouse:down', function(opt) {
    const evt = opt.e
    if (state.isAssetView || this.isDragging) {
      p.$canvas.defaultCursor = 'grabbing'
    }
    if (evt.altKey === true) {
      this.isDragging = true
      this.selection = false
      this.lastPosX = evt.clientX
      this.lastPosY = evt.clientY
      store.dispatch('whiteboarding/setIsFitToScreen', false).then(_.noop)
    }
  })

  p.$canvas.on('mouse:move', function(opt) {
    if (this.isDragging) {
      const e = opt.e
      const vpt = this.viewportTransform
      vpt[4] += e.clientX - this.lastPosX
      vpt[5] += e.clientY - this.lastPosY
      this.requestRenderAll()
      this.lastPosX = e.clientX
      this.lastPosY = e.clientY
      store.dispatch('whiteboarding/setIsFitToScreen', false).then(_.noop)
    }
  })

  p.$canvas.on('mouse:up', function() {
    this.setViewportTransform(this.viewportTransform)
    this.isDragging = false
    this.selection = true
    p.$canvas.defaultCursor = state.isAssetView ? 'grab' : 'default'
  })
}

const $_addSocketListeners = (state: any) => {
  $_log('Add socket listeners')
  const onWindowClose = () => {
    if (p.$socket) {
      $_leave(state)
      p.$socket.close()
    }
  }
  window.onbeforeunload = onWindowClose
  window.onunload = onWindowClose

  p.$socket.on('error', (error: any) => {
    $_log(`socket-io error: ${error}`, true)
    if (p.$socket.disconnected) {
      $_tryReconnect(state).then(_.noop)
    }
  })
  p.$socket.on('ping', () => $_log('socket-io ping'))
  p.$socket.on('reconnect', (attempt: number) => $_log(`reconnect attempt ${attempt}`))
  p.$socket.on('reconnect_attempt', (attempt: number) => $_log(`reconnect_attempt ${attempt}`))
  p.$socket.on('reconnect_error', (error: any) => $_log(`socket-io reconnect_error: ${error}`, true))

  p.$socket.on('reconnect_failed', (error: any) => {
    $_log(`socket-io reconnect_failed: ${error}`, true)
    if (p.$socket.disconnected) {
      $_tryReconnect(state).then(_.noop)
    }
  })

  p.$socket.on('join', (userId: number) => {
    store.commit('whiteboarding/onJoin', userId)
    $_log(`socket.on join. user_id = ${userId}`)
  })

  p.$socket.on('leave', (userId: number) => {
    store.commit('whiteboarding/onLeave', userId)
    $_log(`socket.on leave: user_id = ${userId}`)
  })

  p.$socket.on('order_whiteboard_elements', (summary: any) => {
    _.each(summary.uuids, (uuid: string) => {
      const object = $_getCanvasElement(uuid)
      if (object) {
        if (summary.direction === 'bringToFront') {
          p.$canvas.bringToFront(object)
        } else if (summary.direction === 'sendToBack') {
          p.$canvas.sendToBack(object)
        }
      }
    })
    p.$canvas.requestRenderAll()
    $_log('socket.on order_whiteboard_elements')
  })

  p.$socket.on('update_whiteboard', (data: any) => {
    store.commit('whiteboarding/onWhiteboardUpdate', data)
    $_log('socket.on update_whiteboard')
  })

  p.$socket.on('upsert_whiteboard_elements', (data: any) => {
    const promises: any[] = []
    const whiteboardElements: any[] = []
    _.each(data, (whiteboardElement: any) => {
      promises.push(new Promise<void>((resolve: any) => {
        const element = whiteboardElement.element
        const uuid = whiteboardElement.uuid
        const existing: any = $_getCanvasElement(uuid)
        if (existing) {
          // Deactivate the current group if any of the updated elements are in the current group
          $_deactivateGroupIfOverlap(uuid)
          updatePreviewImage(element, state, uuid).then((modified: boolean) => {
            modified ||= $_assignIn(existing, element)
            if (modified) {
              $_assignIn(existing, element)
              $_ensureWithinCanvas(existing)
              whiteboardElements.push({
                assetId: whiteboardElement.assetId,
                element,
                uuid
              })
            }
            resolve()
          })
        } else {
          $_deserializeElement(state, element).then((e: any) => {
            // Add the element to the whiteboard canvas and move it to its appropriate index
            store.commit('whiteboarding/pushRemoteUUID', e.uuid)
            p.$canvas.add(e)
            resolve()
          })
        }
      }))
    })
    Promise.all(promises).then(() => {
      $_log(`socket.on upsert_whiteboard_elements: uuids = ${_.map(whiteboardElements, 'uuid')}`)
      store.dispatch('whiteboarding/onWhiteboardElementsUpsert', whiteboardElements).then(() => {
        p.$canvas.requestRenderAll()
        setCanvasDimensions(state)
      })
    })
  })

  p.$socket.on('delete_whiteboard_elements', (uuids: string[]) => {
    _.each(uuids, uuid => {
      const element = $_getCanvasElement(uuid)
      if (element) {
        // Deactivate the current group if any of the deleted elements are in the current group
        $_deactivateGroupIfOverlap(uuid)
        p.$canvas.remove(element)
      }
    })
    store.commit('whiteboarding/onDeleteWhiteboardElements', uuids)
    p.$canvas.requestRenderAll()
    // Recalculate the size of the whiteboard canvas
    setCanvasDimensions(state)
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
          const activeObject = p.$canvas.getActiveObject()
          if (activeObject) {
            const clipboard: any[] = []
            const copy = (element: any, left: number, top: number) => {
              const clone = _.cloneDeep(element)
              delete clone.uuid
              clone.left = left
              clone.top = top
              clipboard.push(clone.toObject())
            }
            if (activeObject.type === constants.FABRIC_MULTIPLE_SELECT_TYPE) {
              _.each(activeObject.getObjects(), (object: any) => {
                copy(object, activeObject.left + object.left, activeObject.top + object.top)
              })
            } else {
              copy(activeObject, activeObject.left, activeObject.top)
            }
            if (clipboard.length) {
              store.dispatch('whiteboarding/setClipboard', clipboard).then(_.noop)
            }
          }
        } else if (event.keyCode === 86 && event.metaKey && state.clipboard) {
          $_paste(state)
        }
      }
    }
    element.addEventListener('keydown', onKeydown, false)
  }
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

const $_broadcastDelete = (uuids: string[], state: any) => {
  $_log(`Delete whiteboard elements: ${uuids}`)
  store.commit('whiteboarding/onDeleteWhiteboardElements', uuids)
  const apiCall = () => deleteWhiteboardElement(p.$socket.id, uuids, state.whiteboard.id)
  $_invokeWithSocketConnectRetry('whiteboard element delete', apiCall, state)
}

const $_broadcastUpsert = (whiteboardElements: any[], state: any) => {
  $_log('Upsert whiteboard elements')
  return new Promise<void>(resolve => {
    const whiteboardId = state.whiteboard.id
    const apiCall = () => upsertWhiteboardElements(p.$socket.id, whiteboardElements, whiteboardId).then((data: any) => {
      store.dispatch('whiteboarding/onWhiteboardElementsUpsert', data).then(resolve)
    })
    $_invokeWithSocketConnectRetry('whiteboard elements upsert', apiCall, state)
  })
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

const $_deserializeElement = (state: any, element: any) => {
  return new Promise<Object>(resolve => {
    element = _.cloneDeep(element)
    $_log(`Deserialize ${element.type} element (uuid: ${element.uuid})`)
    if (state.disableAll) {
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
  _.each(p.$canvas.getObjects(), (element: any) => {
    element.evented = enabled
    element.selectable = enabled
  })
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
  if (!state.whiteboard.deletedAt) {
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
  if (state.isAssetView) {
    p.$canvas.defaultCursor = 'grab'
  }
}

const $_initFabricPrototypes = (state: any) => {
  $_log('Init fabric prototypes')
  fabric.Object.prototype.toObject = (function(toObject) {
    // Extend the Fabric.js `toObject` deserialization function to include the property that
    // uniquely identifies an object on the canvas, as well as a property containing the index
    // of the object relative to the other items on the canvas.
    return function() {
      const extras = {
        assetId: this.assetId,
        fontSize: this.fontSize,
        fontFamily: this.fontFamily,
        height: this.height,
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
      if (text) {
        setMode('move')
        // The text element existed before. Notify the server that the element was updated
        const days_until_retirement = $_getDaysUntilRetirement()
        if (days_until_retirement === 0) {
          element.text = 'Sorry, SuiteC is past its expiration date. Please rebuild it, in Perl. Thank you.'
        } else if (text.toLowerCase() === 'when will teena retire?') {
          element.text = `${days_until_retirement} days until freedom`
        }
        element.uuid = element.uuid || uuidv4()
        const whiteboardElements = $_translateIntoWhiteboardElements([element])
        $_broadcastUpsert(whiteboardElements, state).then(_.noop)
      } else {
        const uuid = element.get('uuid')
        p.$canvas.remove(element)
        if (uuid) {
          $_broadcastDelete([uuid], state)
        }
      }
    }
  })
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
  p.$socket.on('close', () => $_tryReconnect(state))
  p.$socket.on('connect_error', (error: any) => {
    $_log(`socket.on connect_error: ${error}`, true)
    $_tryReconnect(state).then(_.noop)
  })
  p.$socket.on('connect_timeout', data => $_log(`[WARN] connect_timeout: ${data}`, true))
  p.$socket.on('connect', () => {
    $_log(`socket.on connect ${p.$socket.id}`)
    const engine: any = p.$socket.io.engine
    if (engine && engine.transport) {
      engine.once('upgrade', () => $_log(`socket.engine.once -> upgrade: ${engine.transport.name}`))
      engine.on('close', (reason: string) => $_log(`socket.engine.on -> close: ${reason}`))
    }
    $_join(state).then(_.noop)
  })
}

function $_invokeWithSocketConnectRetry(description: string, operation: () => void, state: any) {
  const isConnected = () => p.$socket.connected && p.$socket.id
  if (isConnected()) {
    return operation()
  } else {
    $_tryReconnect(state).then(() => {
      if (isConnected()) {
        return operation()
      } else {
        throw `Socket.io reconnect failed prior to ${description}.`
      }
    })
  }
}

const $_join = (state: any) => {
  return new Promise<void>(resolve => {
    $_log('Join')
    store.dispatch('whiteboarding/onJoin', p.$currentUser.id).then(() => {
      p.$socket.emit('join', {whiteboardId: state.whiteboard.id})
      resolve()
    })
  })
}

const $_leave = (state: any) => {
  $_log('Leave')
  const args = {
    userId: p.$currentUser.id,
    whiteboardId: state.whiteboard.id
  }
  p.$socket.emit('leave', args, () => p.$socket = p.$socket.disconnect())
}

const $_log = (statement: string, force?: boolean) => {
  if (p.$config.socketIoDebugMode || force) {
    console.log(`🪲 ${statement}`)
  }
}

const $_paste = (state: any): void => {
  $_log('Paste')
  if (state.clipboard.length) {
    p.$canvas.discardActiveObject()
    const promises: any[] = []
    const whiteboardElements: any[] = []
    let zIndex = Math.max(_.map(state.whiteboard.whiteboardElements, 'zIndex')) + 1
    _.each(state.clipboard, element => {
      if (element.type !== constants.FABRIC_MULTIPLE_SELECT_TYPE) {
        promises.push(new Promise<void>((resolve: any) => {
          const clone = _.cloneDeep(element)
          const uuid = uuidv4()
          clone.evented = true
          clone.left = clone.left + constants.PASTE_OFFSET
          clone.top = clone.top + constants.PASTE_OFFSET
          clone.uuid = uuid
          $_deserializeElement(state, clone).then((object: any) => {
            p.$canvas.add(object)
            whiteboardElements.push({
              assetId: clone.assetId,
              element: clone,
              uuid,
              zIndex
            })
            zIndex++
            resolve()
          })
        }))
      }
    })
    Promise.all(promises).then(() => {
      setCanvasDimensions(state)
      $_broadcastUpsert(whiteboardElements, state).then(_.noop)
    })
  }
}

const $_renderWhiteboard = (state: any, redrawElements?: boolean) => {
  return new Promise<void>(resolve => {
    $_log('Render whiteboard')
    const whiteboardElements = state.whiteboard.whiteboardElements
    const objects: any[] = []
    const done = () => {
      return new Promise<void>(resolve => {
        _.each(_.sortBy(objects, (object: any) => object.zIndex), o => p.$canvas.add(o.element))
        _.each(p.$canvas.getObjects(), $_ensureWithinCanvas)
        // Deactivate all elements and element selection when the whiteboard is being rendered in read-only mode.
        if (state.disableAll) {
          p.$canvas.discardActiveObject()
          p.$canvas.selection = false
        }
        // Render whiteboard and its elements. Set canvas size once all layout changes have been applied.
        setTimeout(() => {
          setCanvasDimensions(state)
          resolve()
        }, 0)
      })
    }
    if (redrawElements && whiteboardElements.length) {
      const promises: any[] = []
      _.each(whiteboardElements, (whiteboardElement: any) => {
        promises.push(new Promise<void>((resolve: any) => {
          $_deserializeElement(state, whiteboardElement.element).then((deserialized: any) => {
            objects.push({element: deserialized, zIndex: whiteboardElement.zIndex})
            resolve()
          })
        }))
      })
      Promise.all(promises).then(() => done().then(resolve))
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

const $_translateIntoWhiteboardElement = (fabricObject: any) => {
  const element = fabricObject.toObject()
  // Force serialization to include properties that fabric.js assumes by default aren't worth its while.
  if (fabricObject.fontSize) {
    element.fontSize = fabricObject.fontSize
  }
  return {assetId: fabricObject.assetId, element: element, uuid: fabricObject.uuid}
}

const $_translateIntoWhiteboardElements = (fabricObjects: any) => {
  return _.map(fabricObjects, (fabricObject: any) => $_translateIntoWhiteboardElement(fabricObject))
}

const $_tryReconnect = (state: any) => {
  return new Promise<void>(resolve => {
    $_log('Try reconnect')
    setTimeout(() => {
      $_leave(state)
      p.$socket.connect((error: any) => {
        if (error) {
          $_log(`socket.connect error: ${error}`, true)
          $_tryReconnect(state).then(() => $_join(state).then(resolve))
        } else {
          $_join(state).then(resolve)
        }
      })
    }, 2000)
  })
}

const $_zoom = (delta: number) => {
  const originalZoom = p.$canvas.getZoom()
  let newZoom = originalZoom * (0.999 ** delta)
  if (newZoom > 20) {
    newZoom = 20
  } else if (newZoom < 0.01) {
    newZoom = 0.01
  }
  p.$canvas.setZoom(newZoom)
  p.$canvas.setHeight(p.$canvas.height * newZoom / originalZoom)
  p.$canvas.setWidth(p.$canvas.width * newZoom / originalZoom)
  p.$canvas.requestRenderAll()
  store.dispatch('whiteboarding/setIsFitToScreen', false).then(_.noop)
}
