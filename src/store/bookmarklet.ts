import {getCategories} from '@/api/categories'

const state = {
  categories: undefined,
  pageMetadata: undefined,
  selectedImages: undefined,
  targetPage: {
    images: undefined,
    metadata: undefined
  },
  workflow: 'linkAsset'
}

const getters = {
  categories: (state: any): any[] => state.categories,
  selectedImages: (state: any): any[] => state.selectedImages,
  targetPage: (state: any): any => state.targetPage,
  workflow: (state: any): string => state.workflow
}

const mutations = {
  setCategories: (state: any, categories: any[]) => state.categories = categories,
  setSelectedImages: (state: any, selectedImages: any[]) => state.selectedImages = selectedImages,
  setTargetPage: (state: any, targetPage: any) => state.targetPage = targetPage,
  setWorkflow: (state: any, workflow: string) => state.workflow = workflow
}

const actions = {
  init: ({commit}) => {
    // The images and metadata of the target webpage are serialized and passed to this component via window.open(...)
    // That window.open() call can be found in the javascript snippet in BookmarkletStep3. That same javascript snippet
    // the user drags to the toolbar when "installing" the SuiteC bookmarklet.
    const target = JSON.parse(window.name)
    commit('setTargetPage', {
      images: target.images,
      metadata: {
        description: target.description,
        title: target.title,
        url: target.url
      }
    })
    return getCategories(false).then(data => commit('setCategories', data))
  },
  setSelectedImages: ({commit}, selectedImages: any[]) => commit('setSelectedImages', selectedImages),
  setWorkflow: ({commit}, workflow: string) => commit('setWorkflow', workflow)
}

export default {
  namespaced: true,
  state,
  getters,
  mutations,
  actions
}
