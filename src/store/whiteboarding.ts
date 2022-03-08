import _ from 'lodash'
import {createWhiteboardElement, getWhiteboard} from '@/api/whiteboards'

const defaultFabricElementBase = {
  backgroundColor: 'lightblue',
  fill: 'rgb(0,0,0)'
}

const $_findElement = (state: any, uid: number) => _.find(state.board.elements, ['uid', uid])

const state = {
  board: undefined,
  fabricElementTemplates: {
    canvas: {
      height: window.innerHeight - 50,
      type: 'canvas',
      width: window.innerWidth
    },
    draw: {
      ...defaultFabricElementBase,
      ...{
        lineWidth: 1,
        type: 'draw'
      }
    },
    ellipsis: {
      ...defaultFabricElementBase,
      ...{
        type: 'ellipsis'
      }
    },
    shape: {
      ...defaultFabricElementBase,
      ...{
        shape: 'Rect:thin',
        type: 'shape'
      }
    },
    text: {
      ...defaultFabricElementBase,
      ...{
        fontSize: 14,
        text: '',
        type: 'text'
      }
    }
  },
  disableAll: true,
  unsavedFabricElement: undefined,
  windowHeight: window.innerHeight,
  windowWidth: window.innerWidth
}

const getters = {
  board: (state: any): any => state.board,
  disableAll: (state: any): boolean => state.disableAll,
  fabricElementTemplates: (state: any): any => state.fabricElementTemplates,
  unsavedFabricElement: (state: any): any => state.unsavedFabricElement,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}

const mutations = {
  add: (state: any, element: any) => state.board.elements.push(element),
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  setBoard: (state: any, whiteboard: any) => state.board = whiteboard,
  setDisableAll: (state: any, disableAll: boolean) => state.disableAll = disableAll,
  setUnsavedFabricElement: (state: any, unsavedFabricElement: any) => state.unsavedFabricElement = unsavedFabricElement,
  updateUnsavedFabricElement: (state: any, {key, value}) => state.unsavedFabricElement[key] = value
}

const actions = {
  saveElement: ({commit, state}: any, element: any) => {
    return new Promise<Object>(resolve => {
      commit('setDisableAll', true)
      return createWhiteboardElement(element, state.board.id)
      .then(data => _.get(data, 'element'))
      .then(element => {
        commit('add', element)
        commit('setDisableAll', false)
        return resolve(element)
      })
    })
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
        const elementJsons = _.map(state.board.elements, 'element')
        if (_.find(elementJsons, ['type', 'canvas'])) {
          done()
        } else {
          return createWhiteboardElement(
            state.fabricElementTemplates.canvas,
            state.board.id
          ).then(data => _.get(data, 'element')).then(done)
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
