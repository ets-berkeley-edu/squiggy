import _ from 'lodash'
import constants from '@/store/whiteboarding/constants'
import store from '@/store'
import Vue from 'vue'
import {getCategories} from '@/api/categories'
import {getWhiteboard} from '@/api/whiteboards'
import {
  initialize,
  setCanvasDimensions,
  updatePreviewImage,
  zoom
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
  if (force) {
    console.log(`🪲 ${statement}`)
  }
}

const state = {
  categories: undefined,
  disableAll: false,
  // Variable that will keep track of whether a shape is currently being drawn
  isAssetView: undefined,
  isDrawingShape: false,
  isFitToScreen: true,
  isInitialized: false,
  // Keep track of whether the currently selected elements are in the process of being moved, scaled or rotated.
  isModifyingElement: false,
  isScrollingCanvas: false,
  mode: 'move',
  remoteUUIDs: [],
  selected: _.clone(DEFAULT_TOOL_SELECTION),
  // Variable that will keep track of the point at which drawing a shape started
  viewport: undefined,
  whiteboard: undefined,
  windowHeight: undefined,
  windowWidth: undefined
}

const getters = {
  categories: (state: any): any[] => state.categories,
  disableAll: (state: any): boolean => state.disableAll || store.getters['context/isLoading'],
  isFitToScreen: (state: any): boolean => state.isFitToScreen,
  isModifyingElement: (state: any): boolean => state.isModifyingElement,
  isScrollingCanvas: (state: any): boolean => state.isScrollingCanvas,
  mode: (state: any): string => state.mode,
  selected: (state: any): any => state.selected,
  whiteboard: (state: any): any => state.whiteboard
}

const mutations = {
  initialize: (state: any, resolve: any) => initialize(state).then(resolve),
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
      const promises: any[] = []
      _.each(whiteboard.whiteboardElements, (whiteboardElement: any) => {
        promises.push(new Promise<boolean>((resolve: any) => {
          updatePreviewImage(whiteboardElement.element, state, whiteboardElement.uuid).then(resolve)
        }))
      })
      Promise.all(promises).then((values: boolean[]) => {
        if (values.includes(true)) {
          setCanvasDimensions(state)
        }
        resolve()
      })
    } else {
      resolve()
    }
  },
  resetSelected: (state: any) => state.selected = _.clone(DEFAULT_TOOL_SELECTION),
  setCategories: (state: any, categories: any[]) => state.categories = categories,
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setIsInitialized: (state: any, isInitialized: boolean) => state.isInitialized = isInitialized,
  setIsScrollingCanvas: (state: any, isScrollingCanvas: boolean) => state.isScrollingCanvas = isScrollingCanvas,
  setViewport: (state: any, viewport: any) => state.viewport = viewport,
  setWhiteboard: (state: any, whiteboard: any) => {
    state.whiteboard = whiteboard
    state.isAssetView = !!state.whiteboard.assetType
    _.each(whiteboard.users, user => {
      if (user.id === p.$currentUser.id) {
        user.isOnline = true
        return false
      }
    })
  },
  updateSelected: (state: any, properties: any) => _.assignIn(state.selected, properties),
  setIsFitToScreen: (state: any, isFitToScreen) => {
    state.isFitToScreen = isFitToScreen
    $_log(`isFitToScreen: ${state.isFitToScreen}`)
  }
}

const actions = {
  init: ({commit}, {whiteboard, disable}) => {
    return new Promise<void>(resolve => {
      getCategories(false).then(categories => {
        commit('setCategories', categories)
        if (disable || whiteboard.deletedAt) {
          commit('setDisableAll', true)
        }
        commit('setWhiteboard', whiteboard)
        commit('setViewport', document.getElementById(constants.VIEWPORT_ELEMENT_ID))
        commit('initialize', resolve)
      })
    })
  },
  refreshWhiteboard: ({commit, state}) => {
    return new Promise<void>(resolve => {
      getWhiteboard(state.whiteboard.id).then((data: any) => {
        commit('refreshWhiteboard', {resolve, whiteboard: data})
      })
    })
  },
  resetSelected: ({commit}) => commit('resetSelected'),
  setIsFitToScreen: ({commit}, isFitToScreen: boolean) => commit('setIsFitToScreen', isFitToScreen),
  toggleFitToScreen: ({commit, state}) => {
    commit('setIsFitToScreen', !state.isFitToScreen)
    setCanvasDimensions(state)
  },
  updateSelected: ({commit}, properties: any) => commit('updateSelected', properties),
  zoomIn: () => zoom(-constants.ZOOM_INCREMENT),
  zoomOut: () => zoom(constants.ZOOM_INCREMENT)
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
