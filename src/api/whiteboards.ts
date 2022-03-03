import axios from 'axios'
import utils from '@/api/api-utils'

export function createWhiteboard(title, userIds) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/create`, {title, userIds})
}

export function deleteWhiteboard(whiteboardId) {
  return axios.delete(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/delete`)
}

export function getWhiteboard(id, socketId?) {
  let url = `${utils.apiBaseUrl()}/api/whiteboard/${id}`
  if (socketId) {
    url += `?socketId=${socketId}`
  }
  return axios.get(url)
}

export function getWhiteboards(
  includeDeleted,
  keywords,
  limit,
  offset,
  orderBy,
  userId
) {
  const data = {
    includeDeleted,
    keywords,
    limit,
    offset,
    orderBy,
    userId
  }
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboards`, data)
}

export function updateWhiteboard(title, whiteboardId) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/update`, {whiteboardId, title})
}
