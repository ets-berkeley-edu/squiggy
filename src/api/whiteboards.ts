import axios from 'axios'
import utils from '@/api/api-utils'

export function createWhiteboardElements(whiteboardElements: any[], whiteboardId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/elements/create`, {
    whiteboardElements,
    whiteboardId,
  })
}

export function createWhiteboard(title: string, userIds: number[]) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/create`, {title, userIds})
}

export function deleteWhiteboard(whiteboardId: number) {
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
  includeDeleted: boolean,
  keywords: string,
  limit: number,
  offset: number,
  orderBy: string,
  userId: number
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

export function updateWhiteboard(title: string, whiteboardId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/update`, {whiteboardId, title})
}

export function updateWhiteboardElement(
  key: string,
  uid: string,
  value: any,
) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/element/update`, {key, uid, value})
}
