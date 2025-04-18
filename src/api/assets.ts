import axios from 'axios'
import utils from '@/api/api-utils'

export function getAsset(assetId) {
  return axios.get(`${utils.apiBaseUrl()}/api/asset/${assetId}`)
}

export function getAssets(params) {
  return axios.post(
    `${utils.apiBaseUrl()}/api/assets`,
    params
  )
}
