import _ from 'lodash'
import {getAssets} from '@/api/assets'

const orderByDefault = 'recent'

function $_search(commit, state, addToExisting?: boolean) {
  return new Promise(resolve => {
    getAssets(
      state.assetType,
      state.categoryId,
      state.keywords,
      state.limit,
      state.offset,
      state.orderBy,
      state.sectionId,
      state.userId
    ).then(data => {
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
  categoryId: undefined,
  isDirty: false,
  keywords: undefined,
  limit: 20,
  offset: 0,
  orderBy: orderByDefault,
  sectionId: undefined,
  totalAssetCount: undefined,
  userId: undefined
}

const getters = {
  assets: (state: any): any[] => state.assets,
  assetType: (state: any): string => state.assetType,
  categoryId: (state: any): number => state.categoryId,
  isDirty: (state: any): boolean => state.isDirty,
  keywords: (state: any): string => state.keywords,
  limit: (state: any): number => state.limit,
  orderBy: (state: any): string => state.orderBy,
  orderByDefault: (): string => orderByDefault,
  totalAssetCount: (state: any): number => state.totalAssetCount,
  userId: (state: any): number => state.userId
}

const mutations = {
  addAssets: (state: any, assets: any[]) => state.assets.push(...assets),
  setAssets: (state: any, assets: any[]) => state.assets = assets,
  setAssetType: (state: any, assetType: string) => {
    state.assetType = assetType
    state.isDirty = true
  },
  setCategoryId: (state: any, categoryId: number) => {
    state.categoryId = categoryId
    state.isDirty = true
  },
  setDirty: (state: any, dirty: boolean) => state.isDirty = dirty,
  setKeywords: (state: any, keywords: string) => {
    state.keywords = keywords
    state.isDirty = true
  },
  setOffset: (state: any, offset: number) => state.offset = offset,
  setOrderBy: (state: any, orderBy: string) => {
    state.orderBy = orderBy
    state.isDirty = true
  },
  setUserId: (state: any, userId: number) => {
    state.userId = userId
    state.isDirty = true
  },
  setTotalAssetCount: (state: any, count: number) => state.totalAssetCount = count,
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
  nextPage: ({commit, state}) => {
    commit('setOffset', state.offset + state.limit)
    return $_search(commit, state, true)
  },
  resetSearch: ({commit}) => commit('setOffset', 0),
  search: ({commit, state}) => $_search(commit, state),
  setAssetType: ({commit}, assetType) => commit('setAssetType', assetType),
  setCategoryId: ({commit}, categoryId) => commit('setCategoryId', categoryId),
  setKeywords: ({commit}, keywords) => commit('setKeywords', keywords),
  setOrderBy: ({commit}, orderBy) => commit('setOrderBy', orderBy),
  setUserId: ({commit}, userId) => commit('setUserId', userId),
  updateAssetStore: ({commit}, updatedAsset) => commit('updateAssetStore', updatedAsset)
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
}
