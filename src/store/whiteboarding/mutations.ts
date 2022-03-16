import _ from 'lodash'
import fabricator from '@/store/whiteboarding/fabricator'
import listeners from '@/store/whiteboarding/listeners'
import stateDefault from '@/store/whiteboarding/state-default'
import utils from '@/api/api-utils'
import Vue from 'vue'

const p = Vue.prototype

export default {
  add: (state: any, whiteboardElement: any) => state.whiteboard.whiteboardElements.push(whiteboardElement),
  addAsset: (state: any, asset: any) => {
    fabricator.addAsset(asset, state)
  },
  afterCanvasRender: (state: any) => {
    if (!state.isModifyingElement && p.$canvas.getActiveObject() || p.$canvas.getActiveGroup()) {
      // Get the bounding rectangle around the currently selected element(s)
      let bound: any
      if (p.$canvas.getActiveObject()) {
        bound = p.$canvas.getActiveObject().getBoundingRect()
      } else if (p.$canvas.getActiveGroup()) {
        bound = p.$canvas.getActiveGroup().getBoundingRect()
      }
      if (bound) {
        // Explicitly draw the bounding rectangle
        p.$canvas.contextContainer.strokeStyle = '#0295DE'
        p.$canvas.contextContainer.strokeRect(bound.left - 10, bound.top - 10, bound.width + 20, bound.height + 20)
      }

      // Position the buttons to modify the selected element(s)
      const editButtons = document.getElementById('whiteboards-board-editelement')
      if (editButtons) {
        editButtons.style.left = (bound.left - 10) + 'px'
        editButtons.style.top = (bound.top + bound.height + 15) + 'px'
      }
    }
  },
  deleteActiveElements: ({state}) => fabricator.deleteActiveElements(state),
  exportAsPng: ({state}, event: any) => {
    // Export the whiteboard to a PNG file
    // event: Click event
    // Return true if whiteboard export is initiated
    if (state.isExportingAsPng || p.$canvas.getObjects().length === 0) {
      event.preventDefault()
      return false
    }
    // Indicate that the server is generating the PNG file
    state.isExportingAsPng = true

    // TODO:
    const $cookies = {
      get: _.noop,
      remove: _.noop
    }
    // Once the user has started receiving the PNG file, a cookie will be set. As long
    // as that cookie isn't set, the "Download as image" button should be disabled
    const cookieName = 'whiteboard.' + state.downloadId + '.png'
    const stopWatching = state.$watch(function() {
      return $cookies.get(cookieName)
    }, function(newValue) {
      if (newValue) {
        // The file started downloading, the "Download as image" button can now be enabled
        state.isExportingAsPng = false
        // Remove the cookie as it's no longer required
        $cookies.remove(cookieName)
        // Generate a new download id for the next time the user clicks the download image button
        state.downloadId = new Date().getTime()
        state.exportPngUrl = `${utils.apiBaseUrl()}/whiteboards/${state.whiteboard.id}/export/png?downloadId=${state.downloadId}`
        // Remove the watch as it's no longer required
        stopWatching()
      }
    })
  },
  init: (state: any, whiteboard: any) => {
    _.assignIn(state, stateDefault)
    state.whiteboard = whiteboard
    state.exportPngUrl = `${utils.apiBaseUrl()}/whiteboards/${whiteboard.id}/export/png?downloadId=${state.downloadId}`
    state.sidebarExpanded = !whiteboard.deletedAt
    state.viewport = document.getElementById('whiteboard-container')
    listeners.addSocketListeners(state)
    listeners.addModalListeners()

    /**
     * TODO: Detect keydown events in the whiteboard to respond to keyboard shortcuts
     */
    // state.viewport.addEventListener('keydown', (event: any) => {
    //   // Remove the selected elements when the delete or backspace key is pressed
    //   if (event.keyCode === 8 || event.keyCode === 46) {
    //     fabricator.deleteActiveElements(state)
    //     event.preventDefault()
    //   } else if (event.keyCode === 67 && event.metaKey) {
    //     // Copy the selected elements
    //     state.clipboard = fabricator.getActiveElements(p.$canvas)
    //   } else if (event.keyCode === 86 && event.metaKey) {
    //     // listeners.Paste the copied elements
    //     fabricator.paste(state)
    //   }
    // }, false)

    // Recalculate the size of the p.$canvas when the window is resized
    window.addEventListener('resize', () => fabricator.setCanvasDimensions(state))
    // TODO:
    // The whiteboard p.$canvas should be initialized only after our additions are made to Fabric prototypes.
    //   initializers.initFabricCanvas(state)
    //   listeners.addFabricCanvasListenters(state)
    fabricator.extendFabricObjects(state)
  },
  moveLayer: (state: any, direction: string) => {
    /**
     * Send the currently selected element(s) to the back or  bring the
     * currently selected element(s) to the front
     *
     * direction: `front` if the currently selected element(s) should be brought to the front, `back` if the currently selected element(s) should be sent to the back
     */
    // Get the selected element(s)
    const elements: any[] = fabricator.getActiveElements()

    // Sort the selected elements by their position to ensure that
    // they are in the same order when moved to the back or front
    elements.sort((elementA: any, elementB: any) => {
      if (direction === 'back') {
        return elementB.index - elementA.index
      } else {
        return elementA.index - elementB.index
      }
    })
    // Move the elements to the back or front one by one
    p.$canvas.remove(p.$canvas.getActiveGroup())
    p.$canvas.deactivateAll().requestRenderAll()
    _.each(elements, (e: any) => {
      const element = fabricator.getCanvasElement(e.uuid)
      if (direction === 'back') {
        element.sendToBack()
      } else if (direction === 'front') {
        element.bringToFront()
      }
    })
    // Notify the server about the updated layers
    p.$canvas.requestRenderAll()
    fabricator.updateLayers(state)

    // When only a single item was selected, re-select it
    if (elements.length === 1) {
      p.$canvas.setActiveObject(fabricator.getCanvasElement(elements[0].uuid))
    }
  },
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  restoreWhiteboard: (state: any) => state.whiteboard.deletedAt = null,
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setDrawMode: (state: any, drawMode: boolean) => p.$canvas.isDrawingMode = drawMode,
  setIsModifyingElement: (state: any, isModifyingElement: boolean) => state.isModifyingElement = isModifyingElement,
  setMode: (state: any, mode: string) => {
    state.mode = mode
    // Deactivate the currently selected item
    p.$canvas.deactivateAll().requestRenderAll()
    // Disable drawing mode
    p.$canvas.isDrawingMode = false
    // Prevent the p.$canvas items from being modified unless
    // the whitnableCanvasElements(false, state)
    if (state.mode === 'move') {
      fabricator.enableCanvasElements(true)
      // TODO: closePopovers()
    } else if (state.mode === 'draw') {
      // Draw mode has been selected
      p.$canvas.isDrawingMode = true
    } else if (state.mode === 'text') {
      // Text mode has been selected
      // Change the cursor to text mode
      // TODO: This doesn't appear to work
      p.$canvas.cursor = 'text'
    }
  },
  setUnsavedFabricElement: (state: any, unsavedFabricElement: any) => state.unsavedFabricElement = unsavedFabricElement,
  toggleSidebar: (state: any, sidebarMode: string) => {
    // Toggle the view mode in the sidebar. If the sidebar was hidden, it will be shown
    // in the requested mode. If the sidebar was shown in a different mode, it will be switched to
    // the requested mode. If the sidebar was shown in the requested mode, it will be hidden again.
    state.sidebarMode = sidebarMode
    state.sidebarExpanded = state.sidebarExpanded && state.sidebarMode === sidebarMode
    // Recalculate the size of the whiteboard p.$canvas. `setTimeout`
    // is required to ensure that the sidebar has collapsed/expanded
    setTimeout(() => fabricator.setCanvasDimensions(state), 0)
  },
  toggleZoom: (state: any) => {
    state.fitToScreen = !state.fitToScreen
    fabricator.setCanvasDimensions(state)
  },
  updateUnsavedFabricElement: (state: any, {key, value}) => state.unsavedFabricElement[key] = value
}
