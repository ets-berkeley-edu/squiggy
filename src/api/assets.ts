import _ from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'

export function getAsset(assetId) {
  return axios.get(`${utils.apiBaseUrl()}/api/asset/${assetId}`)
}

export function getAssets(domain, courseSiteId, args={}) {
  let url = `${utils.apiBaseUrl()}/api/${domain}/${courseSiteId}/assets?`
  _.each(args, (value, key) => url += `${key}=${value}&`)
  return axios.get(url)
}

export function createLinkAsset(categoryIds, description, title, url) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/create`, {
    categoryIds,
    description,
    title,
    type: 'link',
    url
  })
}
