import 'vuetify/dist/vuetify.min.css'
import _ from 'lodash'
import axios from 'axios'
import moment from 'moment-timezone'
import router from './router'
import App from './App.vue'
import store from './store'
import Vue from 'vue'
import VueAnnouncer from '@vue-a11y/announcer'
import VueKinesis from 'vue-kinesis'
import VueMoment from 'vue-moment'
import vuetify from './plugins/vuetify'

const apiBaseUrl = process.env.VUE_APP_API_BASE_URL
const isDebugMode = _.trim(process.env.VUE_APP_DEBUG).toLowerCase() === 'true'

const putFocusNextTick = (id, cssSelector) => {
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

// Vue prototype
Vue.prototype.$_ = _
Vue.prototype.$loading = (noSpinner?: boolean) => store.dispatch('context/loadingStart', noSpinner)
Vue.prototype.$putFocusNextTick = putFocusNextTick
Vue.prototype.$ready = (label, focusTarget?) => store.dispatch('context/loadingComplete', {label, focusTarget})

Vue.use(VueAnnouncer)
Vue.use(VueMoment, {moment})
Vue.use(VueKinesis)

const axiosErrorHandler = error => {
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
}

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
          axiosErrorHandler(error)
          return Promise.reject(error)
        })
      } else {
        axiosErrorHandler(error)
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

axios.get(`${apiBaseUrl}/api/profile/my`).then(data => {
  Vue.prototype.$currentUser = data

  const user = Vue.prototype.$currentUser
  if (user.isAuthenticated) {
    // LTI integration
    axios.defaults.headers['Squiggy-Course-Site-UUID'] = `${user.canvasApiDomain}|${user.canvasCourseId}`
  }

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
})
