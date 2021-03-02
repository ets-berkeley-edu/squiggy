import Vue from 'vue'

const state = {
  loading: undefined
}

const getters = {
  loading: (state: any): boolean => state.loading
}

const mutations = {
  loadingComplete: (state: any, pageTitle: string) => {
    document.title = `${pageTitle || 'UC Berkeley'} | SuiteC`
    state.loading = false
    if (pageTitle) {
      state.screenReaderAlert = `${pageTitle} page is ready`
    }
    Vue.prototype.$putFocusNextTick('page-title')
  },
  loadingStart: (state: any) => (state.loading = true)
}

const actions = {
  loadingComplete: ({commit}, pageTitle) => commit('loadingComplete', pageTitle),
  loadingStart: ({commit}) => commit('loadingStart')}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
