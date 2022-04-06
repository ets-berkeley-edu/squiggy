import _ from 'lodash'
import apiUtils from '@/api/api-utils'
import Vue from 'vue'
import {createWhiteboardElements, getWhiteboard, restoreWhiteboard} from '@/api/whiteboards'
import {
  addAsset,
  deleteActiveElements,
  enableCanvasElements,
  initFabricCanvas,
  moveLayer,
  setCanvasDimensions
} from '@/store/whiteboarding/fabric-utils'

const p = Vue.prototype

const state = {
  // Variable that will keep track of the copied element(s)
  activeCanvasObject: undefined,
  clipboard: [],
  debugLog: '',
  disableAll: true,
  downloadId: undefined,
  exportPngUrl: undefined,
  fitToScreen: true,
  // Variable that will keep track of whether a shape is currently being drawn
  isDrawingShape: false,
  isExportingAsPng: false,
  // Keep track of whether the currently selected elements are in the process of being moved, scaled or rotated.
  isModifyingElement: false,
  isScrollingCanvas: false,
  mode: 'move',
  selected: {},
  sidebarExpanded: false,
  // Variable that will keep track of the point at which drawing a shape started
  startShapePointer: null,
  viewport: undefined,
  whiteboard: undefined
}

const getters = {
  activeCanvasObject: (state: any): any => state.activeCanvasObject,
  disableAll: (state: any): boolean => state.disableAll,
  isModifyingElement: (state: any): boolean => state.isModifyingElement,
  mode: (state: any): string => state.mode,
  onlineUsers: (state: any): any[] => _.filter(state.whiteboard.members, {online: true}),
  selected: (state: any): any => state.selected,
  selectedAsset: () => null,
  whiteboard: (state: any): any => state.whiteboard,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}

const mutations = {
  add: (state: any, whiteboardElement: any) => state.whiteboard.whiteboardElements.push(whiteboardElement),
  addAsset: (state: any, asset: any) => {
    addAsset(asset, state)
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
      const editButtons = document.getElementById('whiteboard-element-edit')
      if (editButtons) {
        editButtons.style.left = (bound.left - 10) + 'px'
        editButtons.style.top = (bound.top + bound.height + 15) + 'px'
      }
    }
  },
  deleteActiveElements: (state: any) => deleteActiveElements(state),
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
        state.exportPngUrl = `${apiUtils.apiBaseUrl()}/whiteboards/${state.whiteboard.id}/export/png?downloadId=${state.downloadId}`
        // Remove the watch as it's no longer required
        stopWatching()
      }
    })
  },
  init: (state: any, whiteboard: any) => {
    _.assignIn(state, {
      whiteboard: whiteboard,
      downloadId: $_createDownloadId(),
      exportPngUrl: `${apiUtils.apiBaseUrl()}/whiteboards/${whiteboard.id}/export/png?downloadId=${state.downloadId}`,
      sidebarExpanded: !whiteboard.deletedAt,
      viewport: document.getElementById('whiteboard-viewport')
    })
    initFabricCanvas(state, whiteboard)
  },
  moveLayer: (state: any, direction: string) => moveLayer(direction, state),
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  resetSelected: (state: any) => state.selected = {},
  restoreWhiteboard: (state: any) => state.whiteboard.deletedAt = null,
  setActiveCanvasObject: (state: any, activeCanvasObject: any) => state.activeCanvasObject = _.cloneDeep(activeCanvasObject),
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setIsModifyingElement: (state: any, isModifyingElement: boolean) => {
    console.log(state, `isModifyingElement = ${isModifyingElement}`)
    state.isModifyingElement = isModifyingElement
  },
  setIsScrollingCanvas: (state: any, isScrollingCanvas: boolean) => state.isScrollingCanvas = isScrollingCanvas,
  setMode: (state: any, mode: string) => {
    // Deactivate the currently selected item
    p.$canvas.discardActiveObject().requestRenderAll()

    p.$canvas.isDrawingMode = false
    // Prevent the p.$canvas items from being modified unless the whitnableCanvasElements(false, state)
    if (mode === 'move') {
      enableCanvasElements(true)
      // TODO:
      // closePopovers()
    } else if (mode === 'draw') {
      // Draw mode has been selected
      p.$canvas.isDrawingMode = true
    } else if (mode === 'text') {
      // Change the cursor to text mode
      p.$canvas.cursor = 'text'
    }
    state.mode = mode
  },
  toggleSidebar: (state: any) => {
    state.sidebarExpanded = !state.sidebarExpanded
    // Recalculate the size of the whiteboard p.$canvas. `setTimeout` is required to ensure that the sidebar has collapsed/expanded.
    setTimeout(() => setCanvasDimensions(state), 0)
  },
  toggleZoom: (state: any) => {
    state.fitToScreen = !state.fitToScreen
    setCanvasDimensions(state)
  },
  updateSelected: (state: any, properties: any) => _.assignIn(state.selected, properties),
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
      scope: scope,
      template: '/app/whiteboards/addlinkmodal/addlinkmodal.html'
    })
    // Switch the toolbar back to move mode. This will also close the add asset popover
    commit('setMode', 'move')
  },
  afterCanvasRender: ({commit}) => commit('afterCanvasRender'),
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
          container: '#whiteboards-board-notifications',
          content: 'This board has been successfully added to the <strong>Asset Library</strong>.',
          duration: 5,
          keyboard: true,
          show: true,
          templateUrl: 'whiteboards-notification-template',
          type: 'success'
        })
      }
      this.$hide()
    }
    // Open the export as asset modal dialog
    $modal({
      scope: scope,
      templateUrl: '/app/whiteboards/exportasassetmodal/exportasasset.html'
    })
    // Switch the toolbar back to move mode. This will also close the add asset popover
    commit('setMode', 'move')
  },
  getObjectAttribute: ({state}, {key, uuid}) => {
    const object = $_findElement(state, uuid)
    return object && object.get(key)
  },
  getSelectedAsset: () => $_getSelectedAsset(),
  getSelectedAssetParams: () => {
    // Get the parameters required to construct the URL to the asset detail page of the currently selected asset element.
    const assetId = $_getSelectedAsset()
    if (assetId) {
      return {
        // TODO:
        // 'api_domain': launchParams.apiDomain,
        // 'course_id': launchParams.courseId,
        // 'tool_url': launchParams.toolUrl,
        assetId: assetId,
        whiteboard_referral: true
      }
    }
  },
  init: ({commit}, whiteboardId: number) => {
    return getWhiteboard(whiteboardId).then(whiteboard => {
      commit('init', whiteboard)
    })
  },
  moveLayer: ({commit}, direction: string) => commit('moveLayer', direction),
  resetSelected: ({commit}) => commit('resetSelected'),
  restoreWhiteboard: ({commit, state}) => {
    if (state.whiteboard && state.whiteboard.deletedAt) {
      return restoreWhiteboard(state.whiteboard.id).then(function() {
        // Update local state
        commit('restoreWhiteboard')
        // Show a notification indicating the whiteboard was restored
        $_alert({
          container: '#whiteboards-board-notifications',
          content: 'The whiteboard has been restored.',
          duration: 5,
          keyboard: true,
          show: true,
          templateUrl: 'whiteboards-notification-template',
          type: 'success'
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
  setActiveCanvasObject: ({commit}, activeCanvasObject: any) => commit('setActiveCanvasObject', activeCanvasObject),
  setDisableAll: ({commit}, disableAll: boolean) => commit('setDisableAll', disableAll),
  setIsModifyingElement: ({commit}, isModifyingElement: boolean) => commit('setIsModifyingElement', isModifyingElement),
  setIsScrollingCanvas: ({commit}, isScrollingCanvas: boolean) => commit('setIsScrollingCanvas', isScrollingCanvas),
  setMode: ({commit}, mode: string) => commit('setMode', mode),
  toggleZoom: ({commit}) => commit('toggleZoom'),
  updateSelected: ({commit}, properties: any) => commit('updateSelected', properties),
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
  actions,
  mutations
}

const $_alert = _.noop

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

const $modal = _.noop

const $_findElement = (state: any, uuid: number) => _.find(state.board.whiteboardElements, ['uuid', uuid])

const $_getSelectedAsset = (): any => {
  // Get the id of the currently selected asset element.
  const selectedElement = p.$canvas.getActiveObject()
  if (selectedElement) {
    return selectedElement.assetId
  }
}
