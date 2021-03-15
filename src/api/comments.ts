import axios from 'axios'
import utils from '@/api/api-utils'

export function createComment(assetId, body, parentId?) {
  return axios.post(`${utils.apiBaseUrl()}/api/comment/create`, {
    assetId,
    body,
    parentId
  })
}

export function getComments(assetId) {
  return axios.get(`${utils.apiBaseUrl()}/api/comments/${assetId}`)
}
