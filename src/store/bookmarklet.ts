import _ from 'lodash'
import Vue from 'vue'
import {getCategories} from '@/api/categories'

const state = {
  assetsCreated: undefined,
  categories: undefined,
  course: undefined,
  isAuthorized: undefined,
  pageMetadata: undefined,
  selectedImages: [],
  targetPage: {
    images: undefined,
    metadata: undefined
  },
  workflow: 'linkAsset'
}

const getters = {
  assetsCreated: (state: any): any[] => state.assetsCreated,
  categories: (state: any): any[] => state.categories,
  course: (state: any): any => state.course,
  isAuthorized: (state: any): boolean => state.isAuthorized,
  selectedImages: (state: any): any[] => state.selectedImages,
  targetPage: (state: any): any => state.targetPage,
  workflow: (state: any): string => state.workflow
}

const mutations = {
  setAssetsCreated: (state: any, assetsCreated: any[]) => state.assetsCreated = assetsCreated,
  setCategories: (state: any, categories: any[]) => state.categories = categories,
  setCourse: (state: any, course: any) => state.course = course,
  setIsAuthorized: (state: any, isAuthorized: boolean) => state.isAuthorized = isAuthorized,
  setSelectedImages: (state: any, selectedImages: any[]) => state.selectedImages = selectedImages,
  setTargetPage: (state: any, targetPage: any) => state.targetPage = targetPage,
  setWorkflow: (state: any, workflow: string) => state.workflow = workflow
}

const actions = {
  init: ({commit, state}) => {
    // The images and metadata of the target webpage are serialized and passed to this component via window.open(...)
    // That window.open() call can be found in the javascript snippet in BookmarkletStep3. That same javascript snippet
    // the user drags to the toolbar when "installing" the SuiteC bookmarklet.
    const target = JSON.parse(window.name)
    const course = _.get(target, 'course')
    commit('setCourse', course)
    commit('setIsAuthorized', course && course.id === _.get(Vue.prototype.$currentUser, 'course.id'))
    if (state.isAuthorized) {
      commit('setTargetPage', {
        images: target.images,
        metadata: {
          description: target.description,
          title: target.title,
          url: target.url
        }
      })
      return getCategories(false).then(data => commit('setCategories', data))
    } else {
      return Promise.reject('Unauthorized')
    }
  },
  setAssetsCreated: ({commit}, assetsCreated: any[]) => commit('setAssetsCreated', assetsCreated),
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
