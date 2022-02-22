import axios from 'axios'
import utils from '@/api/api-utils'

export function createWhiteboard(title, userIds) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/create`, {title, userIds})
}

export function deleteWhiteboard(whiteboardId) {
  return axios.delete(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/delete`)
}

export function getWhiteboards(includeDeleted, limit, offset, orderBy) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboards`, {includeDeleted, limit, offset, orderBy})
}

export function updateWhiteboard(title, whiteboardId) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/update`, {whiteboardId, title})
}
