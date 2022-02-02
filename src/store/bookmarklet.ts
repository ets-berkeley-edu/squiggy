import {getCategories} from '@/api/categories'

const state = {
  categories: undefined,
  images: undefined,
  pageMetadata: undefined
}

const getters = {
  categories: (state: any): any => state.categories,
  images: (state: any): any => state.images,
  pageMetadata: (state: any): any => state.pageMetadata
}

const mutations = {
  setCategories: (state: any, categories: any) => state.categories = categories,
  setImages: (state: any, images: any) => state.images = images,
  setPageMetadata: (state: any, pageMetadata: any) => state.pageMetadata = pageMetadata
}

const actions = {
  init: ({commit}) => {
    // The images and metadata of the target webpage are serialized and passed to this component via window.open(...)
    // That window.open() call can be found in the javascript snippet in BookmarkletStep3. That same javascript snippet
    // the user drags to the toolbar when "installing" the SuiteC bookmarklet.
    const target = JSON.parse(window.name)
    commit('setImages', target.images)
    commit('setPageMetadata', {
      description: target.description,
      title: target.title,
      url: target.url
    })
    return getCategories(false).then(data => commit('setCategories', data))
  },
  setMode: ({commit}, mode: string) => commit('setMode', mode)
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
