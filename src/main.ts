import 'vuetify/dist/vuetify.min.css'
import _ from 'lodash'
import axios from 'axios'
import router from './router'
import Squiggy from './Squiggy.vue'
import store from './store'
import Vue from 'vue'
import vuetify from './plugins/vuetify'

// Axios
axios.defaults.withCredentials = true

// Vue prototype
Vue.prototype.$_ = _

new Vue({
  router,
  store,
  vuetify,
  render: h => h(Squiggy),
}).$mount('#app')
