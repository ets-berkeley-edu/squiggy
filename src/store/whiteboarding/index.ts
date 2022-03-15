import _ from 'lodash'
import constants from '@/store/whiteboarding/constants'
import fabric from 'fabric'
import utils from '@/api/api-utils'
import {createWhiteboardElements, getWhiteboard, restoreWhiteboard} from '@/api/whiteboards'
import initializers from '@/store/whiteboarding/initializers'
import listeners from '@/store/whiteboarding/listeners'
import fabricator from '@/store/whiteboarding/fabricator'

// Depending on the size of the whiteboard, exporting it to PNG can sometimes take a while. To
// prevent the user from clicking the button twice when waiting to get a response, the button
// will be disabled as soon as its clicked. Once the file has been downloaded, it will be
// re-enabled. However, there are no cross-browser events that expose whether a file has been
// downloaded. The PNG export endpoint works around this by taking in a `downloadId` parameter
// and using that to construct a predictable cookie name. When a user clicks the button, the UI
// will disable the button and wait until the cookie is set before re-enabling it again
const downloadId = new Date().getTime()

const $_alert = _.noop
const $modal = _.noop

const $_findElement = (state: any, uuid: number) => _.find(state.board.whiteboardElements, ['uuid', uuid])

const $_getSelectedAsset = (state: any): any => {
  // Get the id of the currently selected asset element.
  const selectedElement = state.canvas.getActiveObject()
  if (selectedElement) {
    return selectedElement.assetId
  }
}

const state = () => ({
  canvas: new fabric.Canvas('whiteboard-canvas'),
  // Variable that will keep track of the copied element(s)
  clipboard: [],
  colors: constants.COLORS,
  disableAll: true,
  downloadId,
  draw: {
    options: constants.DRAW_OPTIONS,
    selected: {
      lineWidth: constants.DRAW_OPTIONS[0].value,
      color: constants.COLORS[0]
    }
  },
  exportPngUrl: undefined,
  fabric: undefined,
  fitToScreen: true,
  // Variable that will keep track of whether a shape is currently being drawn
  isDrawingShape: false,
  isExportingAsPng: false,
  // Keep track of whether the currently selected elements are in the process of being moved, scaled or rotated.
  isModifyingElement: false,
  mode: 'move',
  modeOptions: constants.MODE_OPTIONS,
  scrollingCanvas: false,
  // Variable that will keep track of the shape that is being added to the whiteboard canvas
  shape: null,
  // Variable that will keep track of the selected shape, style and draw color
  shapeOptions: {
    options: constants.SHAPE_OPTIONS,
    selected: {
      type: constants.SHAPE_OPTIONS[0],
      color: constants.COLORS[0]
    }
  },
  sidebarExpanded: false,
  sidebarMode: 'online',
  socket: undefined,
  // Variable that will keep track of the point at which drawing a shape started
  startShapePointer: null,
  unsavedFabricElement: undefined,
  viewport: undefined,
  whiteboard: undefined,
  text: {
    'options': constants.TEXT_OPTIONS,
    'selected': {
      'size': constants.TEXT_OPTIONS[-1],
      'color': constants.COLORS[0]
    }
  }
})

const getters = {
  whiteboard: (state: any): any => state.whiteboard,
  disableAll: (state: any): boolean => state.disableAll,
  fabricElementTemplates: (state: any): any => state.fabricElementTemplates,
  onlineUsers: (state: any): any[] => _.filter(state.whiteboard.members, {'online': true}),
  unsavedFabricElement: (state: any): any => state.unsavedFabricElement,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}

const mutations = {
  add: (state: any, whiteboardElement: any) => state.whiteboard.whiteboardElements.push(whiteboardElement),
  addAsset: (state: any, asset: any) => {
    fabricator.addAsset(asset, state)
  },
  deleteActiveElements: (state: any) => fabricator.deleteActiveElements(state.canvas),
  exportAsPng: ({state}, event: any) => {
    // Export the whiteboard to a PNG file
    // event: Click event
    // Return true if whiteboard export is initiated
    if (state.isExportingAsPng || state.canvas.getObjects().length === 0) {
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
    state.exportPngUrl = `${utils.apiBaseUrl()}/whiteboards/${whiteboard.id}/export/png?downloadId=${downloadId}`
    state.sidebarExpanded = !whiteboard.deletedAt
    state.viewport = document.getElementById('whiteboard-container')
    state.socket = initializers.initSocket(whiteboard)
    listeners.addSocketListeners(state)
    listeners.addModalListeners(state)
    /**
     * Detect keydown events in the whiteboard to respond to keyboard shortcuts
     */
    state.viewport.addEventListener('keydown', (event: any) => {
      // Remove the selected elements when the delete or backspace key is pressed
      if (event.keyCode === 8 || event.keyCode === 46) {
        fabricator.deleteActiveElements(state)
        event.preventDefault()
      } else if (event.keyCode === 67 && event.metaKey) {
        // Copy the selected elements
        state.clipboard = fabricator.getActiveElements(state.canvas)
      } else if (event.keyCode === 86 && event.metaKey) {
        // listeners.Paste the copied elements
        fabricator.paste(state)
      }
    }, false)
    // Recalculate the size of the state.canvas when the window is resized
    window.addEventListener('resize', () => fabricator.setCanvasDimensions(state))
    // The whiteboard state.canvas should be initialized only after our additions are made to Fabric prototypes.
    initializers.initFabricCanvas(state)
    listeners.addFabricCanvasListenters(state)
    fabricator.extendFabricObjects(state)
  },
  initFabricCanvas: (state: any) => initializers.initFabricCanvas(state),
  moveLayer: (state: any, direction: string) => {
    /**
     * Send the currently selected element(s) to the back or  bring the
     * currently selected element(s) to the front
     *
     * direction: `front` if the currently selected element(s) should be brought to the front, `back` if the currently selected element(s) should be sent to the back
     */
    // Get the selected element(s)
    const elements: any[] = fabricator.getActiveElements(state.canvas)

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
    state.canvas.remove(state.canvas.getActiveGroup())
    state.canvas.deactivateAll().renderAll()
    _.each(elements, (e: any) => {
      const element = fabricator.getCanvasElement(state.canvas, e.uuid)
      if (direction === 'back') {
        element.sendToBack()
      } else if (direction === 'front') {
        element.bringToFront()
      }
    })
    // Notify the server about the updated layers
    state.canvas.renderAll()
    fabricator.updateLayers(state)

    // When only a single item was selected, re-select it
    if (elements.length === 1) {
      state.canvas.setActiveObject(fabricator.getCanvasElement(state.canvas, elements[0].uuid))
    }
  },
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  restoreWhiteboard: (state: any) => state.whiteboard.deletedAt = null,
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setDrawMode: (state: any, drawMode: boolean) => state.canvas.isDrawingMode = drawMode,
  setMode: (state: any, mode: string) => {
    state.mode = mode
    // Deactivate the currently selected item
    state.canvas.deactivateAll().renderAll()
    // Disable drawing mode
    state.canvas.isDrawingMode = false
    // Prevent the state.canvas items from being modified unless
    // the whitnableCanvasElements(false, state)
    if (state.mode === 'move') {
      fabricator.enableCanvasElements(true, state)
      // TODO: closePopovers()
    } else if (state.mode === 'draw') {
      // Draw mode has been selected
      state.canvas.isDrawingMode = true
    } else if (state.mode === 'text') {
      // Text mode has been selected
      // Change the cursor to text mode
      // TODO: This doesn't appear to work
      state.canvas.cursor = 'text'
    }
  },
  setUnsavedFabricElement: (state: any, unsavedFabricElement: any) => state.unsavedFabricElement = unsavedFabricElement,
  toggleSidebar: (state: any, sidebarMode: string) => {
    // Toggle the view mode in the sidebar. If the sidebar was hidden, it will be shown
    // in the requested mode. If the sidebar was shown in a different mode, it will be switched to
    // the requested mode. If the sidebar was shown in the requested mode, it will be hidden again.
    state.sidebarMode = sidebarMode
    state.sidebarExpanded = state.sidebarExpanded && state.sidebarMode === sidebarMode
    // Recalculate the size of the whiteboard state.canvas. `setTimeout`
    // is required to ensure that the sidebar has collapsed/expanded
    setTimeout(() => fabricator.setCanvasDimensions(state), 0)
  },
  toggleZoom: (state: any) => {
    state.fitToScreen = !state.fitToScreen
    fabricator.setCanvasDimensions(state)
  },
  updateUnsavedFabricElement: (state: any, {key, value}) => state.unsavedFabricElement[key] = value
}

const actions = {
  addLink: ({commit, state}) => {
    // Launch the modal that allows for a new link to be added
    // Create a new scope for the modal dialog
    const scope = state.$new(true)
    scope.closeModal = function(asset) {
      if (asset) {
        commit('addAsset', asset)
      }
      this.$hide()
    }
    // Open the add link modal dialog
    _.noop({
      'scope': scope,
      'template': '/app/whiteboards/addlinkmodal/addlinkmodal.html'
    })
    // Switch the toolbar back to move mode. This will also close the add asset popover
    commit('setMode', 'move')
  },
  deleteActiveElements: ({commit}) => commit('deleteActiveElements'),
  editWhiteboard: ({commit}) => {
    // Create a new scope for the modal dialog
    // const scope = state.$new(true)
    // scope.whiteboard = state.whiteboard
    // scope.closeModal = function(updatedWhiteboard) {
    //   if (updatedWhiteboard) {
    //     if (updatedWhiteboard.notFound) {
    //       // TODO: If an edit has removed the user's access, refresh the whiteboard list and close this whiteboard
    //       // if ($window.opener) {
    //       //   $window.opener.refreshWhiteboardList()
    //       // }
    //       // $window.close()
    //       _.noop()
    //     } else {
    //       state.whiteboard = updatedWhiteboard
    //       // TODO: Set the title of the window to the new title of the whiteboard
    //       // $rootScope.header = state.whiteboard.title
    //     }
    //   }
    //   // this.$hide()
    // }
    // TODO: Open the edit whiteboard modal dialog
    // $modal({
    //   'scope': scope,
    //   'template': '/app/whiteboards/edit/edit.html'
    // })
    // Switch the toolbar back to move mode. This will
    // also close any open popovers
    commit('setMode', 'move')
  },
  exportasassetmodal: () => {},
  exportAsAsset: ({commit, state}) => {
    // Launch the modal that allows the current user to export the current whiteboard to the asset library
    // Create a new scope for the modal dialog
    const scope = state.$new(true)
    scope.whiteboard = state.whiteboard
    scope.closeModal = function(asset) {
      if (asset) {
        // Construct the link back to the asset library
        // const assetLibraryLink = '/assetlibrary?api_domain=' + launchParams.apiDomain + '&course_id=' + launchParams.courseId + '&tool_url=' + launchParams.toolUrl
        // Show a notification indicating the whiteboard was exported
        $_alert({
          'container': '#whiteboards-board-notifications',
          'content': 'This board has been successfully added to the <strong>Asset Library</strong>.',
          'duration': 5,
          'keyboard': true,
          'show': true,
          'templateUrl': 'whiteboards-notification-template',
          'type': 'success'
        })
      }
      this.$hide()
    }
    // Open the export as asset modal dialog
    $modal({
      'scope': scope,
      'templateUrl': '/app/whiteboards/exportasassetmodal/exportasasset.html'
    })
    // Switch the toolbar back to move mode. This will also close the add asset popover
    commit('setMode', 'move')
  },
  getObjectAttribute: ({state}, {key, uuid}) => {
    const object = $_findElement(state, uuid)
    return object && object.get(key)
  },
  getSelectedAsset: ({state}) => $_getSelectedAsset(state),
  getSelectedAssetParams: ({state}) => {
    // Get the parameters required to construct the URL to the asset detail page of the currently selected asset element.
    const assetId = $_getSelectedAsset(state)
    if (assetId) {
      return {
        // TODO:
        // 'api_domain': launchParams.apiDomain,
        // 'course_id': launchParams.courseId,
        // 'tool_url': launchParams.toolUrl,
        'assetId': assetId,
        'whiteboard_referral': true
      }
    }
  },
  init: ({commit}, whiteboardId: number) => {
    commit('setDisableAll', true)
    return new Promise<void>(resolve => {
      getWhiteboard(whiteboardId).then(whiteboard => {
        commit('init', whiteboard)
        commit('setDisableAll', false)
        resolve()
      })
    })
  },
  moveLayer: ({commit}, direction: string) => commit('moveLayer', direction),
  restoreWhiteboard: ({commit, state}) => {
    if (state.whiteboard && state.whiteboard.deletedAt) {
      return restoreWhiteboard(state.whiteboard.id).then(function() {
        // Update local state
        commit('restoreWhiteboard')
        // Show a notification indicating the whiteboard was restored
        $_alert({
          'container': '#whiteboards-board-notifications',
          'content': 'The whiteboard has been restored.',
          'duration': 5,
          'keyboard': true,
          'show': true,
          'templateUrl': 'whiteboards-notification-template',
          'type': 'success'
        })
      })
    }
  },
  reuseAsset: ({commit}) => {
    // TODO

    // Launch the modal that allows for an existing asset to be added to whiteboard canvas
    // Create a new scope for the modal dialog
    // var scope = $scope.$new(true);
    // scope.closeModal = function(selectedAssets) {
    //   _.each(selectedAssets, addAsset);
    //   this.$hide();
    //   this.$destroy();
    // };
    // Open the asset selection modal dialog
    // $modal({
    //   'animation': false,
    //   'scope': scope,
    //   'template': '/app/whiteboards/reuse/reuse.html'
    // })
    // Switch the toolbar back to move mode. This will also close the add asset popover
    commit('setMode', 'move')
  },
  saveWhiteboardElements: ({commit, state}: any, whiteboardElements: any[]) => {
    return new Promise<void>(resolve => {
      commit('setDisableAll', true)
      return createWhiteboardElements(whiteboardElements, state.whiteboard.id)
      .then(data => _.get(data, 'element'))
      .then(data => {
        _.each(data, whiteboardElement => commit('add', whiteboardElement))
        commit('setDisableAll', false)
        return resolve()
      })
    })
  },
  toggleZoom: ({commit}) => commit('toggleZoom'),
  uploadFiles: ({commit}) => {
    // TODO: Create a new scope for the modal dialog

    // scope.closeModal = function(assets) {
    //   _.each(assets, addAsset)
    //   this.$hide()
    // }
    // // Open the add link modal dialog
    // $modal({
    //   'scope': scope,
    //   'template': '/app/whiteboards/uploadmodal/uploadmodal.html'
    // })
    // Switch the toolbar back to move mode. This will
    // also close the add asset popover
    commit('setMode', 'move')
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
