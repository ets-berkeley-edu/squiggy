import _ from 'lodash'
import constants from '@/store/whiteboarding/constants'
import store from '@/store'
import Vue from 'vue'
import {getCategories} from '@/api/categories'
import {deleteWhiteboard, getWhiteboard, undelete} from '@/api/whiteboards'
import {
  addAssets,
  afterChangeMode,
  deleteActiveElements,
  initialize,
  changeZOrder,
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
  if (p.$config.isVueAppDebugMode || force) {
    console.log(`🪲 ${statement}`)
  }
}

const state = {
  activeCanvasObject: undefined,
  categories: undefined,
  clipboard: [],
  disableAll: false,
  // Variable that will keep track of whether a shape is currently being drawn
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
  isFitToScreen: (state: any): boolean => state.isFitToScreen,
  isModifyingElement: (state: any): boolean => state.isModifyingElement,
  isScrollingCanvas: (state: any): boolean => state.isScrollingCanvas,
  mode: (state: any): string => state.mode,
  selected: (state: any): any => state.selected,
  selectedAsset: () => null,
  whiteboard: (state: any): any => state.whiteboard
}

const mutations = {
  addAssets: (state: any, assets: any[]) => addAssets(assets, state),
  changeZOrder: (state: any, direction: string) => changeZOrder(direction, state),
  deleteActiveElements: (state: any) => deleteActiveElements(state),
  initialize: (state: any, resolve: any) => initialize(state).then(resolve),
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
  onDeleteWhiteboardElements: (state: any, uuids: string[]) => {
    state.whiteboard.whiteboardElements = _.filter(state.whiteboard.whiteboardElements, w => !uuids.includes(w.uuid))
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
  onWhiteboardUpdate: (state: any, {deletedAt, resolve, title, users}) => {
    document.title = `${title} | SuiteC`
    state.whiteboard.title = title
    // Set 'isOnline' (true or false) on incoming users.
    const previousUsersById = {}
    _.each(state.whiteboard.users, u => previousUsersById[u.id] = u)
    _.each(users, user => {
      const existingUser = previousUsersById[user.id]
      user.isOnline = existingUser && existingUser.isOnline
    })
    state.whiteboard.users = users
    // Whiteboard might have been deleted.
    const hasDeleteStatusChanged = (!state.whiteboard.deletedAt && deletedAt) || (state.whiteboard.deletedAt && !deletedAt)
    if (hasDeleteStatusChanged) {
      state.whiteboard.deletedAt = deletedAt
    }
    state.whiteboard.deletedAt = deletedAt
    // Close browser tab if current user is no longer authorized.
    if (!p.$currentUser.isAdmin && !p.$currentUser.isTeaching) {
      if (state.whiteboard.deletedAt) {
        window.close()
      } else {
        const userIds = _.map(state.whiteboard.users, 'id')
        if (!_.includes(userIds, p.$currentUser.id)) {
          window.close()
        }
      }
    }
    resolve()
    if (hasDeleteStatusChanged) {
      p.$loading()
      location.reload()
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
  resetSelected: (state: any) => state.selected = _.clone(DEFAULT_TOOL_SELECTION),
  setActiveCanvasObject: (state: any, activeCanvasObject: any) => state.activeCanvasObject = _.cloneDeep(activeCanvasObject),
  setCategories: (state: any, categories: any[]) => state.categories = categories,
  setClipboard: (state: any, objects: any[]) => {
    _.each(objects, object => {
      delete object.uuid
    })
    state.clipboard = objects
  },
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
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
  addAssets: ({commit}, assets: any[]) => {
    return new Promise<void>(resolve => {
      commit('addAssets', assets)
      resolve()
    })
  },
  changeZOrder: ({commit}, direction: string) => commit('changeZOrder', direction),
  deleteActiveElements: ({commit}) => commit('deleteActiveElements'),
  deleteWhiteboard: ({commit, state}) => {
    return new Promise<void>(resolve => {
      deleteWhiteboard(p.$socket.id, state.whiteboard.id).then(() => {
        commit('onWhiteboardUpdate', {
          deletedAt: Date(),
          resolve,
          title: state.whiteboard.title,
          users: state.whiteboard.users
        })
      })
    })
  },
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
  onJoin: ({commit}, userId: number) => commit('onJoin', userId),
  onWhiteboardUpdate: ({commit}, whiteboard: any) => {
    return new Promise<void>(resolve => {
      commit('onWhiteboardUpdate', {
        deletedAt: whiteboard.deletedAt,
        resolve,
        title: whiteboard.title,
        users: whiteboard.users
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
  setClipboard: ({commit}, objects: any[]) => commit('setClipboard', objects),
  setDisableAll: ({commit}, disableAll: boolean) => commit('setDisableAll', disableAll),
  setIsFitToScreen: ({commit}, isFitToScreen: boolean) => commit('setIsFitToScreen', isFitToScreen),
  setMode: ({commit}, mode: string) => commit('setMode', mode),
  toggleFitToScreen: ({commit, state}) => {
    commit('setIsFitToScreen', !state.isFitToScreen)
    setCanvasDimensions(state)
  },
  undeleteWhiteboard: ({commit, state}) => {
    return new Promise<void>(resolve => {
      if (state.whiteboard.deletedAt) {
        undelete(p.$socket.id, state.whiteboard.id).then(() => {
          commit('onWhiteboardUpdate', {
            deletedAt: null,
            resolve,
            title: state.whiteboard.title,
            users: state.whiteboard.users
          })
        })
      } else {
        resolve()
      }
    })
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
