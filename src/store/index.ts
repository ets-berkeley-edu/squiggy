import assets from '@/store/assets'
import bookmarklet from '@/store/bookmarklet'
import context from '@/store/context'
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {assets, bookmarklet, context},
  strict: process.env.NODE_ENV !== 'production'
})
