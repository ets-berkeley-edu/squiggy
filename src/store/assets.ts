import _ from 'lodash'
import {getAssets} from '@/api/assets'

const orderByDefault = 'recent'

function $_search(commit, state) {
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
      if (_.isNil(state.assets)) {
        commit('setAssets', assets)
      } else {
        commit('addAssets', assets)
      }
      commit('setTotalAssetCount', _.get(data, 'total'))
      resolve(state.assets)
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
  limit: 20,
  offset: 0,
  orderBy: orderByDefault,
  sectionId: undefined,
  totalAssetCount: undefined,
  userId: undefined
}

const getters = {
  assets: (state: any): boolean => state.assets,
  assetType: (state: any): boolean => state.assetType,
  categoryId: (state: any): number => state.categoryId,
  keywords: (state: any): number => state.keywords,
  limit: (state: any): number => state.limit,
  orderBy: (state: any): string => state.orderBy,
  orderByDefault: (): string => orderByDefault,
  totalAssetCount: (state: any): number => state.totalAssetCount,
  userId: (state: any): number => state.userId
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
  search: ({commit, state}) => $_search(commit, state),
  setAssetType: ({commit}, assetType) => commit('setAssetType', assetType),
  setCategoryId: ({commit}, categoryId) => commit('setCategoryId', categoryId),
  setKeywords: ({commit}, keywords) => commit('setKeywords', keywords),
  setOrderBy: ({commit}, orderBy) => commit('setOrderBy', orderBy),
  setUserId: ({commit}, userId) => commit('setUserId', userId)
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
