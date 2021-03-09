import assets from '@/store/assets'
import context from '@/store/context'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {assets, context},
  strict: process.env.NODE_ENV !== 'production'
})
