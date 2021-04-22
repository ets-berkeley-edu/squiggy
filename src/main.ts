import 'vuetify/dist/vuetify.min.css'
import _ from 'lodash'
import App from './App.vue'
import axios from 'axios'
import linkify from 'vue-linkify'
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
Vue.prototype.$ready = (label, focusTarget?) => store.dispatch('context/loadingComplete', {label, focusTarget})

Vue.use(VueAnnouncer)
Vue.use(VueMoment, {moment})
Vue.use(VueKinesis)

Vue.directive('linkified', linkify)

// Axios
axios.defaults.withCredentials = true
axios.interceptors.response.use(
    response => response.headers['content-type'] === 'application/json' ? response.data : response,
    error => {
      const errorStatus = _.get(error, 'response.status')
      if (_.includes([401, 403], errorStatus)) {
        // Refresh user in case his/her session expired.
        return axios.get(`${apiBaseUrl}/api/profile/my`).then(data => {
          Vue.prototype.$currentUser = data
          utils.axiosErrorHandler(error)
          return Promise.reject(error)
        })
      } else {
        utils.axiosErrorHandler(error)
        return Promise.reject(error)
      }
    })

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
axios.defaults.headers['Squiggy-Canvas-Api-Domain'] = params.get('canvasApiDomain')
axios.defaults.headers['Squiggy-Canvas-Course-Id'] = params.get('canvasCourseId')

// TODO: Remove console logging when all is working well.
console.log('canvasApiDomain = ' + params.get('canvasApiDomain'))
console.log('canvasCourseId = ' + params.get('canvasCourseId'))

axios.get(`${apiBaseUrl}/api/profile/my`).then(data => {
  Vue.prototype.$currentUser = data
  Vue.prototype.$supportsCustomMessaging = _.get(Vue.prototype.$currentUser, 'course.canvas.supportsCustomMessaging')

  const mount = () => {
    axios.get(`${apiBaseUrl}/api/config`).then(data => {
      Vue.prototype.$config = data
      Vue.prototype.$config.apiBaseUrl = apiBaseUrl
      Vue.prototype.$config.isVueAppDebugMode = isDebugMode

      new Vue({
        router,
        store,
        vuetify,
        render: h => h(App),
      }).$mount('#app')
    })
  }
  const isInIframe = !!window.parent.frames.length
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
