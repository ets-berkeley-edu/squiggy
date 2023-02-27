import _ from 'lodash'
import Vue from 'vue'
import {getAssets} from '@/api/assets'
import {getAdvancedAssetSearchOptions} from '@/api/courses'

const orderByDefault = 'recent'

function $_search(commit, state, addToExisting?: boolean) {
  return new Promise(resolve => {
    getAssets({
      assetType: state.assetType,
      categoryId: state.categoryId,
      groupId: state.groupId,
      keywords: state.keywords,
      limit: state.limit,
      offset: state.offset,
      orderBy: state.orderBy,
      section: state.section,
      userId: state.userId
    }).then(data => {
      const assets = _.get(data, 'results')
      commit(addToExisting ? 'addAssets' : 'setAssets', assets)
      commit('setTotalAssetCount', _.get(data, 'total'))
      commit('setDirty', false)
      resolve(data)
    })
  })
}

const state = {
  assets: undefined,
  assetType: undefined,
  canvasGroups: [],
  categories: [],
  categoryId: undefined,
  groupId: undefined,
  isDirty: false,
  keywords: undefined,
  limit: 20,
  offset: 0,
  orderBy: orderByDefault,
  section: undefined,
  sections: [],
  totalAssetCount: undefined,
  userId: undefined,
  users: []
}

const getters = {
  assets: (state: any): any[] => state.assets,
  assetType: (state: any): string => state.assetType,
  categories: (state: any): any[] => state.categories,
  categoryId: (state: any): number => state.categoryId,
  canvasGroups: (state: any): any => state.canvasGroups,
  groupId: (state: any): string[] => state.groupId,
  isDirty: (state: any): boolean => state.isDirty,
  keywords: (state: any): string => state.keywords,
  limit: (state: any): number => state.limit,
  orderBy: (state: any): string => state.orderBy || orderByDefault,
  orderByDefault: (): string => orderByDefault,
  sections: (state: any): string[] => state.sections,
  totalAssetCount: (state: any): number => state.totalAssetCount,
  userId: (state: any): number => state.userId,
  users: (state: any): any[] => state.users
}

const mutations = {
  addAssets: (state: any, assets: any[]) => state.assets.push(...assets),
  setAssets: (state: any, assets: any[]) => state.assets = assets,
  setAssetType: (state: any, assetType: string) => {
    state.assetType = assetType
    state.isDirty = true
  },
  setCategories: (state: any, categories: any[]) => state.categories = categories,
  setCategoryId: (state: any, categoryId: number) => {
    state.categoryId = categoryId
    state.isDirty = true
  },
  setCanvasGroups: (state: any, canvasGroups: any[]) => state.canvasGroups = canvasGroups,
  setDirty: (state: any, dirty: boolean) => state.isDirty = dirty,
  setGroupId: (state: any, groupId: number) => {
    state.groupId = groupId
    state.isDirty = true
  },
  setKeywords: (state: any, keywords: string) => {
    state.keywords = keywords
    state.isDirty = true
  },
  setOffset: (state: any, offset: number) => state.offset = offset,
  setOrderBy: (state: any, orderBy: string) => {
    state.orderBy = orderBy
    state.isDirty = true
  },
  setSection: (state: any, section: string) => {
    state.section = section
    state.isDirty = true
  },
  setUserId: (state: any, userId: number) => {
    state.userId = userId
    state.isDirty = true
  },
  setTotalAssetCount: (state: any, count: number) => state.totalAssetCount = count,
  setUsers: (state: any, users: any[]) => {
    state.users = users
    state.sections = []
    _.each(state.users, (user: any) => {
      _.each(user.canvasCourseSections, (canvasCourseSection: string) => {
        const section = {text: canvasCourseSection, value: canvasCourseSection}
        if (!_.find(state.sections, s => s.value === section.value)) {
          state.sections.push(section)
        }
      })
    })
  },
  updateAssetStore: (state: any, updatedAsset: any) => {
    if (state.assets) {
      _.each(state.assets, asset => {
        if (asset.id === updatedAsset.id) {
          Object.assign(asset, updatedAsset)
        }
      })
    }
  },
}

const actions = {
  initAssetSearchOptions({commit}) {
    return new Promise<void>(resolve => {
      const courseId = Vue.prototype.$currentUser.courseId
      getAdvancedAssetSearchOptions(courseId).then(data => {
        commit('setCanvasGroups', _.get(data, 'canvasGroups'))
        commit('setUsers', _.get(data, 'users'))
        commit('setCategories', _.get(data, 'categories'))
        resolve()
      })
    })
  },
  nextPage: ({commit, state}) => {
    commit('setOffset', state.offset + state.limit)
    return $_search(commit, state, true)
  },
  resetSearch: ({commit}) => commit('setOffset', 0),
  search: ({commit, state}) => $_search(commit, state),
  setAssetType: ({commit}, assetType) => commit('setAssetType', assetType),
  setCategoryId: ({commit}, categoryId) => commit('setCategoryId', categoryId),
  setGroupId: ({commit}, groupId) => commit('setGroupId', groupId),
  setKeywords: ({commit}, keywords) => commit('setKeywords', keywords),
  setOrderBy: ({commit}, orderBy) => commit('setOrderBy', orderBy),
  setUserId: ({commit}, userId) => commit('setUserId', userId),
  setSection: ({commit}, section) => commit('setSection', section),
  updateAssetStore: ({commit}, updatedAsset) => commit('updateAssetStore', updatedAsset)
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
