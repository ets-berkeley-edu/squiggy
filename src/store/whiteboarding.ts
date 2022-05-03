import _ from 'lodash'
import Vue from 'vue'
import {getCategories} from '@/api/categories'
import {deleteWhiteboard, restoreWhiteboard} from '@/api/whiteboards'
import {
  addAsset,
  deleteActiveElements,
  initialize,
  moveLayer,
  onWhiteboardUpdate,
  ping,
  refresh,
  setCanvasDimensions,
  setMode
} from '@/store/whiteboarding/fabric-utils'

const p = Vue.prototype

const state = {
  activeCanvasObject: undefined,
  categories: undefined,
  clipboard: undefined,
  disableAll: true,
  fitToScreen: true,
  // Variable that will keep track of whether a shape is currently being drawn
  isDrawingShape: false,
  // Keep track of whether the currently selected elements are in the process of being moved, scaled or rotated.
  isModifyingElement: false,
  isScrollingCanvas: false,
  mode: 'move',
  selected: {},
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
  disableAll: (state: any): boolean => state.disableAll,
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
    if (p.$currentUser.isAdmin || p.$currentUser.isTeaching) {
      refresh(state)
    } else {
      window.close()
    }
  },
  deleteActiveElements: (state: any) => deleteActiveElements(state),
  init: (state: any, whiteboard: any) => {
    state.whiteboard = whiteboard
    initialize(state)
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
    refresh(state)
  },
  setActiveCanvasObject: (state: any, activeCanvasObject: any) => state.activeCanvasObject = _.cloneDeep(activeCanvasObject),
  setCategories: (state: any, categories: any[]) => state.categories = categories,
  setClipboard: (state: any, object: any) => state.clipboard = object,
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setIsModifyingElement: (state: any, isModifyingElement: boolean) => state.isModifyingElement = isModifyingElement,
  setIsDrawingShape: (state: any, isDrawingShape: boolean) => state.isDrawingShape = isDrawingShape,
  setIsScrollingCanvas: (state: any, isScrollingCanvas: boolean) => state.isScrollingCanvas = isScrollingCanvas,
  setMode: (state: any, mode: string) => setMode(state, mode),
  setStartShapePointer: (state: any, startShapePointer: any) => state.startShapePointer = startShapePointer,
  setUsers: (state: any, users: any[]) => state.whiteboard.users = users,
  toggleSidebar: (state: any) => setTimeout(() => setCanvasDimensions(state), 0),
  toggleZoom: (state: any) => {
    setMode(state, 'zoom')
    state.fitToScreen = !state.fitToScreen
    setCanvasDimensions(state)
  },
  updateSelected: (state: any, properties: any) => _.assignIn(state.selected, properties)
}

const actions = {
  addAsset: ({commit}, asset: any) => commit('addAsset', asset),
  onWhiteboardUpdate: ({commit}, whiteboard: any) => commit('onWhiteboardUpdate', whiteboard),
  deleteActiveElements: ({commit}) => commit('deleteActiveElements'),
  deleteWhiteboard: ({commit, state}) => deleteWhiteboard(state.whiteboard.id).then(() => commit('afterWhiteboardDelete')),
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
  setActiveCanvasObject: ({commit}, activeCanvasObject: any) => commit('setActiveCanvasObject', activeCanvasObject),
  setClipboard: ({commit}, object: any) => commit('setClipboard', object),
  setDisableAll: ({commit}, disableAll: boolean) => commit('setDisableAll', disableAll),
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
