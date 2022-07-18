import _ from 'lodash'
import constants from '@/store/whiteboarding/constants'
import store from '@/store'
import Vue from 'vue'
import {getCategories} from '@/api/categories'
import {deleteWhiteboard, getWhiteboard, restoreWhiteboard} from '@/api/whiteboards'
import {
  addAsset,
  afterChangeMode,
  deleteActiveElements,
  emitWhiteboardUpdate,
  initialize,
  moveLayer,
  reload,
  setCanvasDimensions,
  updatePreviewImage
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
  isInitialized: false,
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
  addAsset: (state: any, asset: any) => addAsset(asset, state),
  afterWhiteboardDelete: (state: any) => {
    state.whiteboard.deletedAt = new Date()
    state.whiteboard.isReadOnly = true
  },
  clearClipboard: (state: any) => state.clipboard = [],
  copy: (state: any, object: any) => state.clipboard.push(object),
  deleteActiveElements: (state: any) => deleteActiveElements(state),
  emitWhiteboardUpdate: (state: any, whiteboard: any) => emitWhiteboardUpdate(state, whiteboard),
  initialize: (state: any, resolve: any) => initialize(state).then(resolve),
  moveLayer: (state: any, direction: string) => moveLayer(direction, state),
  onJoin: (state: any, userId: string) => {
    _.each(state.whiteboard.users, user => {
      if (user.id === userId) {
        user.isOnline = true
        return false
      }
    })
  },
  onLeave: (state: any, userId: string) => {
    _.each(state.whiteboard.users, user => {
      if (user.id === userId) {
        user.isOnline = false
        return false
      }
    })
  },
  onUpdateWhiteboard: (state: any, whiteboard: any) => {
    state.whiteboard.title = whiteboard.title
    const usersPrevious = {}
    _.each(state.whiteboard.users, u => usersPrevious[u.id] = u)
    _.each(whiteboard.users, user => {
      const existingUser = usersPrevious[user.id]
      user.isOnline = existingUser && existingUser.isOnline
    })
    state.whiteboard.users = whiteboard.users
  },
  onWhiteboardElementDelete: (state: any, uuid: string) => {
    state.whiteboard.whiteboardElements = _.filter(state.whiteboard.whiteboardElements, w => w.uuid !== uuid)
  },
  onWhiteboardElementUpsert: (state: any, {assetId, element, uuid}) => {
    const existing = _.find(state.whiteboard.whiteboardElements, ['uuid', uuid])
    element = _.cloneDeep(element)
    if (existing) {
      existing.assetId = assetId
      existing.element = element
    } else {
      state.whiteboard.whiteboardElements.push({assetId, element, uuid})
    }
  },
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  pushRemoteUUID: (state: any, uuid: string) => state.remoteUUIDs.push(uuid),
  refreshWhiteboard: (state: any, {resolve, whiteboard}) => {
    state.whiteboard.deletedAt = whiteboard.deletedAt
    state.whiteboard.title = whiteboard.title
    state.whiteboard.users = whiteboard.users
    const count = whiteboard.whiteboardElements.length
    if (count) {
      let modified = false
      _.each(whiteboard.whiteboardElements, (whiteboardElement: any, index: number) => {
        const uuid = whiteboardElement.uuid
        const after = (index) => {
          if (index === count - 1) {
            if (modified) {
              setCanvasDimensions(state)
            }
            resolve()
          }
        }
        updatePreviewImage(whiteboardElement.element.src, state, uuid).then((wasUpdated: boolean) => {
          modified = wasUpdated
          after(index)
        })
      })
    }
  },
  reload: (state, resolve) => reload(state).then(resolve),
  resetSelected: (state: any) => state.selected = _.clone(DEFAULT_TOOL_SELECTION),
  restoreWhiteboard: (state: any) => {
    state.whiteboard.isReadOnly = false
    state.whiteboard.deletedAt = null
  },
  setActiveCanvasObject: (state: any, activeCanvasObject: any) => state.activeCanvasObject = _.cloneDeep(activeCanvasObject),
  setCanvasDimensions: (state) => setCanvasDimensions(state),
  setCategories: (state: any, categories: any[]) => state.categories = categories,
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setFitToScreen: (state: any, fitToScreen: boolean) => state.fitToScreen = fitToScreen,
  setIsInitialized: (state: any, isInitialized: boolean) => state.isInitialized = isInitialized,
  setIsModifyingElement: (state: any, isModifyingElement: boolean) => state.isModifyingElement = isModifyingElement,
  setIsDrawingShape: (state: any, isDrawingShape: boolean) => state.isDrawingShape = isDrawingShape,
  setIsScrollingCanvas: (state: any, isScrollingCanvas: boolean) => state.isScrollingCanvas = isScrollingCanvas,
  setMode: (state: any, mode: string) => {
    $_log(`Set mode: ${mode}`)
    state.mode = mode
    afterChangeMode(state)
  },
  setStartShapePointer: (state: any, startShapePointer: any) => state.startShapePointer = startShapePointer,
  setViewport: (state: any, viewport: any) => state.viewport = viewport,
  setWhiteboard: (state: any, whiteboard: any) => {
    state.whiteboard = whiteboard
    if (state.whiteboard.isReadOnly) {
      state.disableAll = true
    }
    _.each(whiteboard.users, user => {
      if (user.id === p.$currentUser.id) {
        user.isOnline = true
        return false
      }
    })
  },
  updateSelected: (state: any, properties: any) => _.assignIn(state.selected, properties)
}

const actions = {
  addAsset: ({commit}, asset: any) => commit('addAsset', asset),
  deleteActiveElements: ({commit}) => commit('deleteActiveElements'),
  deleteWhiteboard: ({commit, state}) => {
    return new Promise<void>(resolve => {
      deleteWhiteboard(state.whiteboard.id).then(() => {
        commit('afterWhiteboardDelete')
        if (p.$currentUser.isAdmin || p.$currentUser.isTeaching) {
          commit('reload', resolve)
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
        commit('initialize', resolve)
      })
    })
  },
  moveLayer: ({commit}, direction: string) => commit('moveLayer', direction),
  onJoin: ({commit}, userId: number) => commit('onJoin', userId),
  refreshWhiteboard: ({commit, state}) => {
    return new Promise<void>(resolve => {
      getWhiteboard(state.whiteboard.id).then((data: any) => {
        commit('refreshWhiteboard', {resolve, whiteboard: data})
      })
    })
  },
  resetSelected: ({commit}) => commit('resetSelected'),
  restoreWhiteboard: ({commit, state}) => {
    return new Promise<void>(resolve => {
      if (state.whiteboard.deletedAt) {
        restoreWhiteboard(state.whiteboard.id).then(function() {
          // Update local state
          commit('restoreWhiteboard')
          commit('reload', resolve)
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
    commit('setCanvasDimensions')
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
