import _ from 'lodash'
import router from './router'
import Vue from 'vue'

const $_postIFrameMessage = (generator, callback?) => {
  if (window.parent) {
    const postMessage = () => {
      // Parent will respond to the this embedded call with a message and scroll information.
      if (callback) {
        const eventType = 'message'
        const processor = event => {
          if (event && event.data) {
            try {
              callback(JSON.parse(event.data))
              window.removeEventListener(eventType, processor)
            } catch(error) {
              return false
            }
          }
        }
        window.addEventListener(eventType, processor)
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
}

const $_getUrlParamPerPrefix = (context, key, prefix) => {
  let value
  const url = new URL(context.location)
  if (url.hash && _.includes(url.hash, '=')) {
    const hash = url.hash.replace('#', '')
    const split = hash.split('=')
    if (split[0] === `${prefix}${key}`) {
      value = split[1]
    }
  }
  return value || new URLSearchParams(context.location.search).get(`${prefix}${key}`)
}

const $_getParentUrlParam = key => {
  return new Promise(resolve => {
    // See getParentUrlData() in legacy SuiteC
    const callback = context => {
      const location = _.get(context, 'location')
      return resolve(location ? $_getUrlParamPerPrefix(context, key, 'suitec_') : null)
    }
    $_postIFrameMessage(() => ({subject: 'getParent'}), callback)
  })
}

export default {
  axiosErrorHandler: error => {
    const errorStatus = _.get(error, 'response.status')
    if (Vue.prototype.$currentUser.isAuthenticated) {
      if (errorStatus === 404) {
        router.push({path: '/404'})
      } else if (errorStatus >= 400) {
        router.push({
          path: '/error',
          query: {
            m: _.get(error, 'response.data.message') || error.message || _.get(error, 'response.statusText')
          }
        })
      }
    } else if (!router.currentRoute.meta.isLoginPage) {
      router.push({
        path: '/',
        query: {
          m: 'Your session has expired'
        }
      })
    }
  },
  extractBookmarkId: (to, key) => {
    return new Promise(resolve => {
      if (Vue.prototype.$isInIframe && Vue.prototype.$supportsCustomMessaging) {
        $_getParentUrlParam(key).then(value => resolve(value))
      } else {
        const value = $_getUrlParamPerPrefix(window, key, 'suitec_')
        return resolve(value)
      }
    })
  },
  postIFrameMessage: $_postIFrameMessage,
  putFocusNextTick: (id, cssSelector) => {
    const callable = () => {
        let el = document.getElementById(id)
        el = el && cssSelector ? el.querySelector(cssSelector) : el
        el && el.focus()
        return !!el
    }
    Vue.prototype.$nextTick(() => {
      let counter = 0
      const job = setInterval(() => (callable() || ++counter > 3) && clearInterval(job), 500)
    })
  }
}
