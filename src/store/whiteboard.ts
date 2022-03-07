import _ from 'lodash'
import {createWhiteboardElement, getWhiteboard, updateWhiteboardElement} from '@/api/whiteboards'

const $_createWhiteboardElement = (commit: any, elementType: string, whiteboardId: number) => {
  const element = {
    canvas: {
      backgroundColor: 'green',
      height: window.innerHeight - 50,
      type: 'canvas',
      width: window.innerWidth,
    },
    ellipsis: {
      fill: 'rgb(0,0,0)',
      type: 'ellipsis'
    },
    text: {
      fill: 'rgb(0,0,0)',
      text: '',
      type: 'text'
    }
  }[elementType]
  return createWhiteboardElement(element, whiteboardId).then(data => _.get(data, 'element'))
}

const $_findElement = (state: any, uid: number) => _.find(state.board.elements, ['uid', uid])

const $_getElementJsons = (state: any) => _.map(state.board.elements, 'element')

const state = {
  board: undefined,
  disableAll: true,
  windowHeight: window.innerHeight,
  windowWidth: window.innerWidth
}

const getters = {
  board: (state: any): any => state.board,
  elementJsons: (state: any): any => $_getElementJsons(state),
  disableAll: (state: any): boolean => state.disableAll,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}

const mutations = {
  add: (state: any, element: any) => {
    state.disableAll = true
    state.board.elements.push(element)
  },
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  setBoard: (state: any, whiteboard: any) => state.board = whiteboard,
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setObjectAttribute: (state: any, {key, uid, value}) => {
    updateWhiteboardElement(key, uid, value).then()
  }
}

const actions = {
  add: ({commit, state}: any, elementType: string) => {
    commit('setDisableAll', true)
    const done = (element: any) => {
      commit('setDisableAll', false)
      return element
    }
    return $_createWhiteboardElement(commit, elementType, state.board.id).then(element => commit('add', element)).then(done)
  },
  getObjectAttribute: ({state}, {key, uid}) => {
    const object = $_findElement(state, uid)
    return object && object.get(key)
  },
  init: ({commit, state}, whiteboardId: number) => {
    commit('setDisableAll', true)
    return new Promise<void>(resolve => {
      // TODO: Wire up real socket IO per https://flask-socketio.readthedocs.io/
      const mockSocketId = new Date().getTime()
      getWhiteboard(whiteboardId, mockSocketId).then(whiteboard => {
        commit('setBoard', whiteboard)
        const done = () => {
          commit('setDisableAll', false)
          resolve()
        }
        // const elementJsons = _.map(state.board.elements, 'element')
        const hasCanvas = !!_.find($_getElementJsons(state), ['type', 'canvas'])
        if (hasCanvas) {
          done()
        } else {
          $_createWhiteboardElement(commit, 'canvas', state.board.id).then(element => commit('add', element)).then(done)
        }
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
