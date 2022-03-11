import _ from 'lodash'
import {createWhiteboardElements, getWhiteboard} from '@/api/whiteboards'

const defaultFabricElementBase = {
  fill: 'rgb(0,0,0)'
}

const $_findElement = (state: any, uuid: number) => _.find(state.board.whiteboardElements, ['uuid', uuid])

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
  add: (state: any, whiteboardElement: any) => state.board.whiteboardElements.push(whiteboardElement),
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
  getObjectAttribute: ({state}, {key, uuid}) => {
    const object = $_findElement(state, uuid)
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
        if (_.find(_.map(state.board.whiteboardElements, 'element'), ['type', 'canvas'])) {
          done()
        } else {
          return createWhiteboardElements(
            [{
              element: state.fabricElementTemplates.canvas,
              whiteboardId: state.board.id
            }],
            state.board.id
          ).then(data => _.get(data, 'element')).then(done)
        }
      })
    })
  },
  saveWhiteboardElements: ({commit, state}: any, whiteboardElements: any[]) => {
    return new Promise<void>(resolve => {
      commit('setDisableAll', true)
      return createWhiteboardElements(whiteboardElements, state.board.id)
      .then(data => _.get(data, 'element'))
      .then(data => {
        _.each(data, whiteboardElement => commit('add', whiteboardElement))
        commit('setDisableAll', false)
        return resolve()
      })
    })
  }
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
