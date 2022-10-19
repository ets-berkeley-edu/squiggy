import '@mdi/font/css/materialdesignicons.min.css'
import 'vuetify/dist/vuetify.min.css'
import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import linkifyHtml from 'linkify-html'
import 'linkify-plugin-hashtag'
import HighchartsVue from 'highcharts-vue'
import moment from 'moment-timezone'
import router from './router'
import store from './store'
import utils from './utils'
import Vue from 'vue'
import VueAnnouncer from '@vue-a11y/announcer'
import VueKinesis from 'vue-kinesis'
import VueMoment from 'vue-moment'
import vuetify from './plugins/vuetify'

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL
const isDebugMode = _.trim(process.env.VUE_APP_DEBUG).toLowerCase() === 'true'

// Vue prototype
Vue.prototype.$_ = _
Vue.prototype.$loading = (noSpinner?: boolean) => store.dispatch('context/loadingStart', noSpinner)
Vue.prototype.$putFocusNextTick = utils.putFocusNextTick
Vue.prototype.$ready = (pageTitle, focusTarget?, announcement?) => store.dispatch('context/loadingComplete', {pageTitle, focusTarget, announcement})

const Highcharts = require('highcharts/highcharts')
const HighchartsMore = require('highcharts/highcharts-more')
HighchartsMore(Highcharts)
window.Highcharts = Highcharts

Vue.use(HighchartsVue)
Vue.use(VueAnnouncer)
Vue.use(VueMoment, {moment})
Vue.use(VueKinesis)

const linkifyDirective = (el, binding) => {
  const options = {
    defaultProtocol: 'https'
  }
  _.assign(options, binding.value)
  el.innerHTML = linkifyHtml(el.innerHTML, options)
}
Vue.directive('linkified', linkifyDirective)

// Axios
axios.defaults.withCredentials = true
axios.interceptors.response.use(
  response => response.headers['content-type'] === 'application/json' ? response.data : response,
  error => {
    const errorStatus = _.get(error, 'response.status')
    const requestUrl = _.get(error, 'config.url', '')
    if (_.includes([401, 403], errorStatus)) {
      if (requestUrl.endsWith('/api/profile/my') || requestUrl.endsWith('/api/config')) {
        Vue.prototype.$currentUser = {}
        utils.axiosErrorHandler(error)
        return Promise.resolve(error)
      } else {
        // Refresh user in case his/her session expired.
        return axios.get(`${apiBaseUrl}/api/profile/my`).then(data => {
          Vue.prototype.$currentUser = data
          utils.axiosErrorHandler(error)
          return Promise.reject(error)
        })
      }
    } else {
      utils.axiosErrorHandler(error)
      return Promise.reject(error)
    }
  }
)

// Vue config
Vue.config.productionTip = isDebugMode
Vue.config.errorHandler = function(error, vm, info) {
  console.error(error || info)
  router.push({
    path: '/error',
    query: {
      m: _.get(error, 'message') || info
    }
  })
}

const params = new URLSearchParams(window.location.search)
if (params.get('canvasApiDomain')) {
  axios.defaults.headers['Squiggy-Canvas-Api-Domain'] = params.get('canvasApiDomain')
}
if (params.get('canvasCourseId')) {
  axios.defaults.headers['Squiggy-Canvas-Course-Id'] = params.get('canvasCourseId')
}
const isBookmarklet = !!params.get('_b')
if (isBookmarklet) {
  axios.defaults.headers['Squiggy-Bookmarklet-Auth'] = params.get('_b')
}

const isInIframe = utils.isInIframe()

Vue.prototype.$isInIframe = isInIframe && !isBookmarklet
Vue.prototype.$isBookmarklet = isBookmarklet

axios.get(`${apiBaseUrl}/api/profile/my`).then(data => {
  Vue.prototype.$currentUser = data
  Vue.prototype.$supportsCustomMessaging = _.get(Vue.prototype.$currentUser, 'course.canvas.supportsCustomMessaging')

  const mount = () => {
    axios.get(`${apiBaseUrl}/api/config`).then(data => {
      Vue.prototype.$config = data
      Vue.prototype.$config.apiBaseUrl = apiBaseUrl
      Vue.prototype.$config.isVueAppDebugMode = isDebugMode
      const ebEnvironment = Vue.prototype.$config.ebEnvironment
      Vue.prototype.$config.isProduction = ebEnvironment && ebEnvironment.toLowerCase().includes('prod')

      new Vue({
        router,
        store,
        vuetify,
        render: h => h(App),
      }).$mount('#app')
    })
  }
  if (isInIframe) {
    store.dispatch('context/postIFrameMessage', {
      generator: () => ({
        subject: 'changeParent',
        scrollToTop: true
      })
    }).then(mount)

  } else {
    mount()
  }
})
