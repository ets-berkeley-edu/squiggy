import assets from '@/store/assets'
import bookmarklet from '@/store/bookmarklet'
import context from '@/store/context'
import Vue from 'vue'
import Vuex from 'vuex'
import whiteboarding from '@/store/whiteboarding'
import whiteboards from '@/store/whiteboards'

Vue.use(Vuex)

export default new Vuex.Store({
  modules: {assets, bookmarklet, context, whiteboarding, whiteboards},
  strict: process.env.NODE_ENV !== 'production'
})
