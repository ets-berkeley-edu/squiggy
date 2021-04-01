import _ from 'lodash'
import router from './router'
import Vue from 'vue'

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
  extractBookmarkId: (to, type) => {
    if (to.hash) {
      const match = to.hash.match(new RegExp(`.*#suitec_${type}=(\\d+)`))
      return _.size(match) && match[1]
    } else {
      return null
    }
  },
  postIFrameMessage: (generator, callback?) => {
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
  },
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
