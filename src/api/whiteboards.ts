import axios from 'axios'
import utils from '@/api/api-utils'

export function createWhiteboard(title) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/create`, {title})
}

export function deleteWhiteboard(whiteboardId) {
  return axios.delete(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/delete`)
}

export function getWhiteboards(limit, offset, orderBy) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboards`, {limit, offset, orderBy})
}

export function updateWhiteboard(title, whiteboardId) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/update`, {whiteboardId, title})
}
