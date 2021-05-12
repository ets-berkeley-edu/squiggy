import _ from 'lodash'
import Vue from 'vue'

const $_extractBookmarkHash = context => {
  const bookmarkHash = {}
  const url = new URL(context)
  if (url.hash) {
    const keyPrefix = 'suitec_'
    const params = url.hash.replace('#', '')
    new URLSearchParams(params).forEach((value, key) => {
      const trimmedKey = key.startsWith(keyPrefix) ? key.replace(keyPrefix, '') : null
      if (trimmedKey) {
        bookmarkHash[trimmedKey] = value
      }
    })
  }
  return bookmarkHash
}

const $_getStandaloneBookmarkHash = () => $_extractBookmarkHash(window.location)

const $_getIFrameBookmarkHash = () => {
  return new Promise(resolve => {
    // See getParentUrlData() in legacy SuiteC
    $_postIFrameMessage(
      () => ({subject: 'getParent'}),
      context => resolve($_extractBookmarkHash(context))
    )
  })
}

// eslint-disable-next-line
const $_postIFrameMessage = (generator: () => any, callback?: (data: any) => any) => {
  const postMessage = () => {
    // Parent will respond to the this embedded call with a message and scroll information.
    if (callback) {
      const eventType = 'message'
      const processor = event => {
        console.log('Message event listener called')
        if (event && event.data) {
          try {
            console.log('Event data received')
            console.log(event.data)
            callback(JSON.parse(event.data))
            window.removeEventListener(eventType, processor)
          } catch(error) {
            console.log('Error parsing event data')
            console.log(error)
            return false
          }
        }
      }
      window.addEventListener(eventType, processor)
      console.log('Message event listener added')
    }
    // Send the message to the parent container as a string-ified object
    window.parent.postMessage(JSON.stringify(generator()), '*')
    return true
  }
  Vue.prototype.$nextTick(() => {
    let counter = 0
    const job = setInterval(() => (postMessage() || ++counter > 3) && clearInterval(job), 500)
  })
}

const state = {
  bookmarkValues: {},
  isInIframe: !!window.parent.frames.length,
  isLoading: undefined,
  noSpinnerWhenLoading: false
}

const getters = {
  isInIframe: (state: any): boolean => state.isInIframe,
  isLoading: (state: any): boolean => state.isLoading,
  noSpinnerWhenLoading: (state: any): boolean => state.noSpinnerWhenLoading,
}

const mutations = {
  clearBookmarkHash: () => {
    if (Vue.prototype.$isInIframe && Vue.prototype.$supportsCustomMessaging) {
      $_postIFrameMessage(() => ({
        subject: 'setParentHash',
        hash: ''
      }))
    }
  },
  loadingComplete: (state: any, pageTitle: string, focusTarget?: string) => {
    document.title = `${pageTitle || 'UC Berkeley'} | SuiteC`
    state.isLoading = false
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
  loadingStart: (state: any, noSpinnerWhenLoading?: boolean) => {
    state.isLoading = true
    state.noSpinnerWhenLoading = noSpinnerWhenLoading
  },
  postIFrameMessage: (state: any, generator, callback?) => $_postIFrameMessage(generator, callback),
  rewriteBookmarkHash: (state: any, params: any) => {
    const isInIframe = Vue.prototype.$isInIframe
    const filtered = _.pickBy(params, value => !_.isNil(value))
    const hash = _.map(filtered, (value, key) => `suitec_${key}=${encodeURIComponent(value)}`).join('&')
    if (isInIframe && Vue.prototype.$supportsCustomMessaging) {
      $_postIFrameMessage(() => ({
        subject: 'setParentHash',
        hash: hash
      }))
    } else if (!isInIframe) {
      window.location.hash = hash
    }
  }
}

const actions = {
  clearBookmarkHash: ({commit}) => commit('rewriteBookmarkHash', {}),
  getBookmarkHash: () => {
    return new Promise(resolve => {
      const isInIframe = Vue.prototype.$isInIframe
      if (isInIframe && Vue.prototype.$supportsCustomMessaging) {
        return $_getIFrameBookmarkHash().then(resolve)
      } else if (!isInIframe) {
        return resolve($_getStandaloneBookmarkHash())
      }
    })
  },
  loadingComplete: ({commit}, {label, focusTarget}) => commit('loadingComplete', label, focusTarget),
  loadingStart: ({commit}, noSpinner?: boolean) => commit('loadingStart', noSpinner),
  postIFrameMessage: ({commit}, {generator, callback}) => commit('postIFrameMessage', generator, callback),
  rewriteBookmarkHash: ({commit}, params) => commit('rewriteBookmarkHash', params)
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
