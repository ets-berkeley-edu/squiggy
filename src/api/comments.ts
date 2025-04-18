import axios from 'axios'
import utils from '@/api/api-utils'

export function getComments(assetId) {
  return axios.get(`${utils.apiBaseUrl()}/api/comments/${assetId}`)
}
