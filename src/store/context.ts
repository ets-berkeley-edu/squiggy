import Vue from 'vue'

const state = {
  loading: undefined
}

const getters = {
  loading: (state: any): boolean => state.loading
}

const mutations = {
  loadingComplete: (state: any, pageTitle: string, focusTarget?: string) => {
    document.title = `${pageTitle || 'UC Berkeley'} | SuiteC`
    state.loading = false
    if (pageTitle) {
      Vue.prototype.$announcer.assertive(`${pageTitle} page is ready`)
    }
    if (focusTarget) {
      Vue.prototype.$putFocusNextTick(focusTarget)
    } else {
      const callable = () => {
        const elements = document.getElementsByTagName('h2')
        if (elements.length > 0) {
          elements[0].setAttribute('tabindex', '-1')
          elements[0].focus()
        }
        return elements.length > 0
      }
      Vue.prototype.$nextTick(() => {
        let counter = 0
        const job = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
      })
    }
    Vue.prototype.$putFocusNextTick('page-title')
  },
  loadingStart: (state: any) => (state.loading = true)
}

const actions = {
  loadingComplete: ({commit}, {label, focusTarget}) => commit('loadingComplete', label, focusTarget),
  loadingStart: ({commit}) => commit('loadingStart')}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
