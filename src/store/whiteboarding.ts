import _ from 'lodash'
import Vue from 'vue'
import {getCategories} from '@/api/categories'
import {deleteWhiteboard, restoreWhiteboard} from '@/api/whiteboards'
import {
  addAsset,
  deleteActiveElements,
  enableCanvasElements,
  initFabricCanvas,
  moveLayer,
  onWhiteboardUpdate,
  ping,
  setCanvasDimensions
} from '@/store/whiteboarding/fabric-utils'

const p = Vue.prototype

const state = {
  // Variable that will keep track of the copied element(s)
  activeCanvasObject: undefined,
  categories: undefined,
  clipboard: undefined,
  debugLog: '',
  disableAll: true,
  fitToScreen: true,
  hideSidebar: false,
  // Variable that will keep track of whether a shape is currently being drawn
  isDrawingShape: false,
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
  categories: (state: any): any[] => state.categories,
  disableAll: (state: any): boolean => state.disableAll,
  fitToScreen: (state: any): boolean => state.fitToScreen,
  hideSidebar: (state: any): boolean => state.hideSidebar,
  isModifyingElement: (state: any): boolean => state.isModifyingElement,
  isScrollingCanvas: (state: any): boolean => state.isScrollingCanvas,
  mode: (state: any): string => state.mode,
  selected: (state: any): any => state.selected,
  selectedAsset: () => null,
  whiteboard: (state: any): any => state.whiteboard,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}

const mutations = {
  add: (state: any, whiteboardElement: any) => state.whiteboard.whiteboardElements.push(whiteboardElement),
  addAsset: (state: any, asset: any) => addAsset(asset, state),
  afterWhiteboardDelete: (state: any) => {
    state.whiteboard.isDeleted = true
    state.whiteboard.isReadOnly = true
    if (!p.$currentUser.isAdmin && !p.$currentUser.isTeaching) {
      window.close()
    }
  },
  deleteActiveElements: (state: any) => deleteActiveElements(state),
  init: (state: any, whiteboard: any) => {
    _.assignIn(state, {
      sidebarExpanded: !whiteboard.isReadOnly,
      viewport: document.getElementById('whiteboard-viewport'),
      whiteboard: whiteboard
    })
    initFabricCanvas(state, whiteboard)
  },
  moveLayer: (state: any, direction: string) => moveLayer(direction, state),
  onWhiteboardUpdate: (state: any, whiteboard: any) => onWhiteboardUpdate(state, whiteboard),
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  resetSelected: (state: any) => state.selected = {},
  restoreWhiteboard: (state: any) => {
    state.whiteboard.isReadOnly = false
    state.whiteboard.deletedAt = null
  },
  setActiveCanvasObject: (state: any, activeCanvasObject: any) => state.activeCanvasObject = _.cloneDeep(activeCanvasObject),
  setCategories: (state: any, categories: any[]) => state.categories = categories,
  setClipboard: (state: any, object: any) => state.clipboard = object,
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setHideSidebar: (state: any, hideSidebar: boolean) => state.hideSidebar = hideSidebar,
  setIsModifyingElement: (state: any, isModifyingElement: boolean) => state.isModifyingElement = isModifyingElement,
  setIsDrawingShape: (state: any, isDrawingShape: boolean) => state.isDrawingShape = isDrawingShape,
  setIsScrollingCanvas: (state: any, isScrollingCanvas: boolean) => state.isScrollingCanvas = isScrollingCanvas,
  setMode: (state: any, mode: string) => {
    // Deactivate the currently selected item
    p.$canvas.discardActiveObject().requestRenderAll()
    p.$canvas.isDrawingMode = false
    // Prevent the p.$canvas items from being modified unless the whitnableCanvasElements(false, state)
    if (mode === 'move') {
      enableCanvasElements(true)
      state.disableAll = false
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
  setStartShapePointer: (state: any, startShapePointer: any) => state.startShapePointer = startShapePointer,
  setUsers: (state: any, users: any[]) => state.whiteboard.users = users,
  toggleSidebar: (state: any) => {
    state.sidebarExpanded = !state.sidebarExpanded
    // Recalculate the size of the whiteboard p.$canvas. `setTimeout` is required to ensure that the sidebar has collapsed/expanded.
    setTimeout(() => setCanvasDimensions(state), 0)
  },
  toggleZoom: (state: any) => {
    state.fitToScreen = !state.fitToScreen
    setCanvasDimensions(state)
  },
  updateSelected: (state: any, properties: any) => _.assignIn(state.selected, properties)
}

const actions = {
  addAsset: ({commit}, asset: any) => commit('addAsset', asset),
  onWhiteboardUpdate: ({commit}, whiteboard: any) => commit('onWhiteboardUpdate', whiteboard),
  deleteActiveElements: ({commit}) => commit('deleteActiveElements'),
  deleteWhiteboard: ({commit, state}) => {
    deleteWhiteboard(state.whiteboard.id).then(() => {
      commit('afterWhiteboardDelete')
    })
  },
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
    // $modal({
    //   scope: scope,
    //   templateUrl: '/app/whiteboards/exportasassetmodal/exportasasset.html'
    // })
    // Switch the toolbar back to move mode. This will also close the add asset popover
    commit('setMode', 'move')
  },
  getSelectedAsset: () => $_getSelectedAsset(),
  init: ({commit}, whiteboard: any) => {
    return new Promise(resolve => {
      getCategories(false).then(categories => {
        commit('setCategories', categories)
        commit('init', whiteboard)
        resolve(whiteboard)
      })
    })
  },
  moveLayer: ({commit}, direction: string) => commit('moveLayer', direction),
  ping: ({state}) => ping(state),
  resetSelected: ({commit}) => commit('resetSelected'),
  restoreWhiteboard: ({commit, state}) => {
    return new Promise<void>(resolve => {
      if (state.whiteboard.deletedAt) {
        restoreWhiteboard(state.whiteboard.id).then(function() {
          // Update local state
          commit('restoreWhiteboard')
          resolve()
        })
      } else {
        resolve()
      }
    })
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
  setActiveCanvasObject: ({commit}, activeCanvasObject: any) => commit('setActiveCanvasObject', activeCanvasObject),
  setClipboard: ({commit}, object: any) => commit('setClipboard', object),
  setDisableAll: ({commit}, disableAll: boolean) => commit('setDisableAll', disableAll),
  setHideSidebar: ({commit}, hideSidebar: boolean) => commit('setHideSidebar', hideSidebar),
  setIsDrawingShape: ({commit}, isDrawingShape: boolean) => commit('setIsDrawingShape', isDrawingShape),
  setIsModifyingElement: ({commit}, isModifyingElement: boolean) => commit('setIsModifyingElement', isModifyingElement),
  setIsScrollingCanvas: ({commit}, isScrollingCanvas: boolean) => commit('setIsScrollingCanvas', isScrollingCanvas),
  setMode: ({commit}, mode: string) => commit('setMode', mode),
  setStartShapePointer: ({commit}, startShapePointer: any) => commit('setStartShapePointer', startShapePointer),
  setUsers: ({commit}, users: any[]) => commit('setUsers', users),
  toggleZoom: ({commit}) => commit('toggleZoom'),
  updateSelected: ({commit}, properties: any) => commit('updateSelected', properties)
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}

const $_alert = _.noop

const $_getSelectedAsset = (): any => {
  // Get the id of the currently selected asset element.
  const selectedElement = p.$canvas.getActiveObject()
  if (selectedElement) {
    return selectedElement.assetId
  }
}
