import _ from 'lodash'
import constants from '@/store/whiteboarding/constants'
import store from '@/store'
import Vue from 'vue'
import {getCategories} from '@/api/categories'
import {deleteWhiteboard, restoreWhiteboard} from '@/api/whiteboards'
import {
  addAsset,
  afterChangeMode,
  deleteActiveElements,
  emitWhiteboardUpdate,
  initialize,
  moveLayer,
  refreshPreviewImages,
  reload,
  setCanvasDimensions
} from '@/store/whiteboarding/fabric-utils'

const DEFAULT_TOOL_SELECTION = {
  color: constants.COLORS.black.hex,
  fill: constants.COLORS.black.hex,
  fontSize: constants.TEXT_SIZE_OPTIONS[0].value,
  shape: 'Rect',
  stroke: constants.COLORS.black.hex,
  strokeWidth: 2,
  style: 'thin',
  width: 1
}

const p = Vue.prototype

const $_log = (statement: string, force?: boolean) => {
  if (p.$config.isVueAppDebugMode || force) {
    console.log(`🪲 ${statement}`)
  }
}

const state = {
  activeCanvasObject: undefined,
  categories: undefined,
  clipboard: [],
  disableAll: true,
  fitToScreen: true,
  // Variable that will keep track of whether a shape is currently being drawn
  isDrawingShape: false,
  // Keep track of whether the currently selected elements are in the process of being moved, scaled or rotated.
  isModifyingElement: false,
  isScrollingCanvas: false,
  mode: 'move',
  remoteUUIDs: [],
  selected: _.clone(DEFAULT_TOOL_SELECTION),
  // Variable that will keep track of the point at which drawing a shape started
  startShapePointer: null,
  viewport: undefined,
  whiteboard: undefined,
  windowHeight: undefined,
  windowWidth: undefined
}

const getters = {
  activeCanvasObject: (state: any): any => state.activeCanvasObject,
  categories: (state: any): any[] => state.categories,
  disableAll: (state: any): boolean => state.disableAll || store.getters['context/isLoading'],
  fitToScreen: (state: any): boolean => state.fitToScreen,
  isModifyingElement: (state: any): boolean => state.isModifyingElement,
  isScrollingCanvas: (state: any): boolean => state.isScrollingCanvas,
  mode: (state: any): string => state.mode,
  selected: (state: any): any => state.selected,
  selectedAsset: () => null,
  whiteboard: (state: any): any => state.whiteboard
}

const mutations = {
  add: (state: any, whiteboardElement: any) => state.whiteboard.whiteboardElements.push(whiteboardElement),
  addAsset: (state: any, asset: any) => addAsset(asset, state),
  afterWhiteboardDelete: (state: any) => {
    state.whiteboard.deletedAt = new Date()
    state.whiteboard.isReadOnly = true
  },
  clearClipboard: (state: any) => state.clipboard = [],
  copy: (state: any, object: any) => state.clipboard.push(object),
  deleteActiveElements: (state: any) => deleteActiveElements(state),
  emitWhiteboardUpdate: (state: any, whiteboard: any) => emitWhiteboardUpdate(state, whiteboard),
  join: (state: any, userId: number) => {
    const user = _.find(state.whiteboard.users, ['id', userId])
    if (user) {
      user.isOnline = true
    }
  },
  moveLayer: (state: any, direction: string) => moveLayer(direction, state),
  onJoin: (state: any, userId: string) => {
    _.each(state.whiteboard.users, user => {
      if (user.id === userId) {
        user.isOnline = true
        return false
      }
    })
  },
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  pushRemoteUUID: (state: any, uuid: string) => state.remoteUUIDs.push(uuid),
  resetSelected: (state: any) => state.selected = _.clone(DEFAULT_TOOL_SELECTION),
  restoreWhiteboard: (state: any) => {
    state.whiteboard.isReadOnly = false
    state.whiteboard.deletedAt = null
  },
  setActiveCanvasObject: (state: any, activeCanvasObject: any) => state.activeCanvasObject = _.cloneDeep(activeCanvasObject),
  setCategories: (state: any, categories: any[]) => state.categories = categories,
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setFitToScreen: (state: any, fitToScreen: boolean) => state.fitToScreen = fitToScreen,
  setIsModifyingElement: (state: any, isModifyingElement: boolean) => state.isModifyingElement = isModifyingElement,
  setIsDrawingShape: (state: any, isDrawingShape: boolean) => state.isDrawingShape = isDrawingShape,
  setIsScrollingCanvas: (state: any, isScrollingCanvas: boolean) => state.isScrollingCanvas = isScrollingCanvas,
  setMode: (state: any, mode: string) => {
    $_log(`Set mode: ${mode}`)
    state.mode = mode
    afterChangeMode(state)
  },
  setStartShapePointer: (state: any, startShapePointer: any) => state.startShapePointer = startShapePointer,
  setUsers: (state: any, users: any[]) => state.whiteboard.users = users,
  setViewport: (state: any, viewport: any) => state.viewport = viewport,
  setWhiteboard: (state: any, whiteboard: any) => {
    state.whiteboard = whiteboard
    if (state.whiteboard.isReadOnly) {
      state.disableAll = true
    }
  },
  updateSelected: (state: any, properties: any) => _.assignIn(state.selected, properties)
}

const actions = {
  addAsset: ({commit}, asset: any) => commit('addAsset', asset),
  refreshPreviewImages: ({state}) => refreshPreviewImages(state),
  deleteActiveElements: ({commit}) => commit('deleteActiveElements'),
  deleteWhiteboard: ({commit, state}) => {
    return new Promise<void>(resolve => {
      deleteWhiteboard(state.whiteboard.id).then(() => {
        commit('afterWhiteboardDelete')
        if (p.$currentUser.isAdmin || p.$currentUser.isTeaching) {
          reload(state).then(resolve)
        } else {
          window.close()
          resolve()
        }
      })
    })
  },
  emitWhiteboardUpdate: ({commit}, whiteboard: any) => commit('emitWhiteboardUpdate', whiteboard),
  init: ({commit}, whiteboard: any) => {
    return new Promise<void>(resolve => {
      getCategories(false).then(categories => {
        commit('setCategories', categories)
        commit('setWhiteboard', whiteboard)
        commit('setViewport', document.getElementById(constants.VIEWPORT_ELEMENT_ID))
        initialize(state).then(resolve)
      })
    })
  },
  moveLayer: ({commit}, direction: string) => commit('moveLayer', direction),
  resetSelected: ({commit}) => commit('resetSelected'),
  restoreWhiteboard: ({commit, state}) => {
    return new Promise<void>(resolve => {
      if (state.whiteboard.deletedAt) {
        restoreWhiteboard(state.whiteboard.id).then(function() {
          // Update local state
          commit('restoreWhiteboard')
          reload(state).then(resolve)
        })
      } else {
        resolve()
      }
    })
  },
  setDisableAll: ({commit}, disableAll: boolean) => commit('setDisableAll', disableAll),
  setMode: ({commit}, mode: string) => commit('setMode', mode),
  toggleZoom: ({commit, state}) => {
    commit('setMode', 'zoom')
    commit('setFitToScreen', !state.fitToScreen)
    setCanvasDimensions(state)
  },
  updateSelected: ({commit}, properties: any) => commit('updateSelected', properties)
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
