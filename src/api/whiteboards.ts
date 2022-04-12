import axios from 'axios'
import utils from '@/api/api-utils'

export function createWhiteboard(title: string, userIds: number[]) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/create`, {title, userIds})
}

export function deleteWhiteboard(whiteboardId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/delete`)
}

export function getWhiteboard(id: number) {
  return axios.get(`${utils.apiBaseUrl()}/api/whiteboard/${id}`)
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

export function restoreWhiteboard(whiteboardId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/restore`, {whiteboardId})
}

export function updateWhiteboard(title: string, userIds: number[], whiteboardId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/update`, {title, userIds, whiteboardId})
}
