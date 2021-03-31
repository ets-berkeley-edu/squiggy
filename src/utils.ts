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
      const regex = new RegExp(`#${type}:\\d+`, 'g' )
      let match = to.hash.match(regex)
      match = _.size(match) && match[0].match(/\d+/g)
      return _.size(match) && match[0]
    } else {
      return null
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
