import _ from 'lodash'
import constants from '@/store/whiteboarding/constants'
import store from '@/store'
import Vue from 'vue'
import {fabric} from 'fabric'

const p = Vue.prototype

export function initialize(state: any) {
  $_log('Initialize')
  store.commit('whiteboarding/setIsInitialized', false)
  return new Promise<void>(resolve => {
    $_initCanvas(state)
    $_renderWhiteboard(state, true).then(() => {
      $_enableCanvasElements(false)
      $_addCanvasPanningListeners(state)
      // Recalculate the size of the p.$canvas when the window is resized
      window.addEventListener('resize', () => setCanvasDimensions(state))
      store.commit('whiteboarding/setIsInitialized', true)
      resolve()
    })
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

const $_log = (statement: string, force?: boolean) => {
  if (p.$config.socketIoDebugMode || force) {
    console.log(`🪲 ${statement}`)
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
