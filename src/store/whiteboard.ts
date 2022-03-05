import _ from 'lodash'
import {createWhiteboardElement, getWhiteboard, updateWhiteboardElement} from '@/api/whiteboards'

export function $_findElement(state: any, uid: number) {
  return _.find(state.board.elements, ['uid', uid])
}

const state = {
  board: undefined,
  disableAll: true,
  windowHeight: window.innerHeight,
  windowWidth: window.innerWidth
}

const getters = {
  board: (state: any): any => state.board,
  disableAll: (state: any): boolean => state.disableAll,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}

const mutations = {
  add: (state: any, element: any) => {
    state.disableAll = true
    const done = data => {
      state.board.elements.push(data)
    }
    return createWhiteboardElement(element, state.board.id).then(done)
  },
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setObjectAttribute: (state: any, {key, uid, value}) => {
    updateWhiteboardElement(key, uid, value).then()
  },
  init: (state: any, whiteboard: any) => {
    state.board = {
      ...whiteboard,
      elements: []
    }
  }
}

const actions = {
  addEllipsis: ({commit}) => {
    return commit('add', {
      fill: 'rgb(0,0,0)',
      type: 'ellipsis'
    })
  },
  addText: ({commit}) => {
    return commit('add', {
      fill: 'rgb(0,0,0)',
      type: 'text'
    })
  },
  getObjectAttribute: ({state}, {key, uid}) => {
    const object = $_findElement(state, uid)
    return object && object.get(key)
  },
  init: ({commit}, whiteboardId: number) => {
    return new Promise(resolve => {
      // TODO: Wire up real socket IO per https://flask-socketio.readthedocs.io/
      const mockSocketId = new Date().getTime()
      getWhiteboard(whiteboardId, mockSocketId).then(whiteboard => {
        commit('init', whiteboard)
        commit('setDisableAll', false)
        resolve(state.board)
      })
    })
  },
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
