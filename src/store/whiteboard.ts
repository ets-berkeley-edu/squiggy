import {getWhiteboard} from '@/api/whiteboards'

const state = {
  whiteboard: undefined,
  windowHeight: window.innerHeight,
  windowWidth: window.innerWidth
}

const getters = {
  whiteboard: (state: any): any => state.whiteboard,
  windowHeight: (state: any): number => state.windowHeight,
  windowWidth: (state: any): number => state.windowWidth,
}

const mutations = {
  onWindowResize: (state: any) => {
    state.windowHeight = window.innerHeight
    state.windowWidth = window.innerWidth
  },
  setWhiteboard: (state: any, whiteboard: number) => state.whiteboard = whiteboard,
}

const actions = {
  init: ({commit}, whiteboardId: number) => {
    return new Promise<void>(resolve => {
      // TODO: Wire up real socket IO per https://flask-socketio.readthedocs.io/
      const mockSocketId = new Date().getTime()
      getWhiteboard(whiteboardId, mockSocketId).then(data => {
        commit('setWhiteboard', data)
        resolve()
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
