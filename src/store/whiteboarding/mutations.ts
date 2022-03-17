import _ from 'lodash'
import canvas from '@/store/whiteboarding/utils/canvas'
import FABRIC_MULTIPLE_SELECT_TYPE from '@/store/whiteboarding/utils/constants'
import fabricator from '@/store/whiteboarding/utils/fabricator'
import listeners from '@/store/whiteboarding/utils/listeners'
import stateDefault from '@/store/whiteboarding/utils/state-default'
import utils from '@/api/api-utils'
import Vue from 'vue'
import socket from '@/store/whiteboarding/utils/socket'

const p = Vue.prototype

export default {
  add: (state: any, whiteboardElement: any) => state.whiteboard.whiteboardElements.push(whiteboardElement),
  addAsset: (state: any, asset: any) => {
    fabricator.addAsset(asset, state)
  },
  afterCanvasRender: (state: any) => {
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
    // Reset state
    _.assignIn(state, stateDefault)
    _.assignIn(state, {
      whiteboard: whiteboard,
      downloadId: $_createDownloadId(),
      exportPngUrl: `${utils.apiBaseUrl()}/whiteboards/${whiteboard.id}/export/png?downloadId=${state.downloadId}`,
      sidebarExpanded: !whiteboard.deletedAt,
      viewport: document.getElementById('whiteboard-viewport')
    })
    canvas.init(state)
    listeners.init(state)
    if (!whiteboard.deletedAt) {
      // Open a websocket connection for real-time communication with the server (chat + whiteboard changes) when
      // the whiteboard is rendered in edit mode. The course ID and API domain are passed in as handshake query parameters
      socket.init(state)
    }
    // The whiteboard p.$canvas should be initialized only after our additions are made to Fabric prototypes.
    fabricator.init(state)
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
    const selection = p.$canvas.getActiveObject()
    if (selection.type === FABRIC_MULTIPLE_SELECT_TYPE) {
      p.$canvas.remove(selection)
    }

    p.$canvas.discardActiveObject().requestRenderAll()
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
    p.$canvas.discardActiveObject().requestRenderAll()
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

/**
 * Depending on the size of the whiteboard, exporting it to PNG can sometimes take a while. To
 * prevent the user from clicking the button twice when waiting to get a response, the button
 * will be disabled as soon as its clicked. Once the file has been downloaded, it will be
 * re-enabled. However, there are no cross-browser events that expose whether a file has been
 * downloaded. The PNG export endpoint works around this by taking in a `downloadId` parameter
 * and using that to construct a predictable cookie name. When a user clicks the button, the UI
 * will disable the button and wait until the cookie is set before re-enabling it again
 */
 const $_createDownloadId = () => new Date().getTime()
