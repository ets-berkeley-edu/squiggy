import _ from 'lodash'
import {getAssets} from '@/api/assets'

export function $_search(commit, state) {
  return new Promise<void>(resolve => {
    getAssets(
      state.assetType,
      state.categoryId,
      state.hasComments,
      state.hasLikes,
      state.hasViews,
      state.keywords,
      state.limit,
      state.offset,
      state.orderBy,
      state.sectionId,
      state.userId
    ).then(data => {
      const assets = _.get(data, 'results')
      if (state.offset === 0) {
        commit('setAssets', assets)
      } else {
        commit('addAssets', assets)
      }
      commit('setTotalAssetCount', _.get(data, 'total'))
      resolve(assets)
    })
  })
}

const state = {
  assets: undefined,
  assetType: undefined,
  categoryId: undefined,
  hasComments: undefined,
  hasLikes: undefined,
  hasViews: undefined,
  keywords: undefined,
  limit: 10,
  offset: 0,
  orderBy: 'recent',
  sectionId: undefined,
  totalAssetCount: undefined,
  userId: undefined
}

const getters = {
  assets: (state: any): boolean => state.assets
}

const mutations = {
  addAssets: (state: any, assets: any[]) => state.assets.unshift(...assets.reverse()),
  setAssets: (state: any, assets: any[]) => state.assets = assets,
  setAssetType: (state: any, assetType: string) => state.assetType = assetType,
  setCategoryId: (state: any, categoryId: number) => state.categoryId = categoryId,
  setKeywords: (state: any, keywords: string) => state.keywords = keywords,
  setOffset: (state: any, offset: number) => state.offset = offset,
  setOrderBy: (state: any, orderBy: string) => state.orderBy = orderBy,
  setUserId: (state: any, userId: number) => state.userId = userId,
  setTotalAssetCount: (state: any, count: number) => state.totalAssetCount = count
}

const actions = {
  nextPage: ({commit, state}) => {
    commit('setOffset', state.offset + state.limit)
    return $_search(commit, state)
  },
  search: ({commit}, {
    assetType,
    categoryId,
    keywords,
    orderBy,
    userId
  }: any) => {
    commit('setAssetType', assetType)
    commit('setCategoryId', categoryId)
    commit('setKeywords', keywords)
    commit('setOffset', 0)
    commit('setOrderBy', orderBy)
    commit('setUserId', userId)
    return $_search(commit, state)
  }
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
