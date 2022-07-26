import axios from 'axios'
import utils from '@/api/api-utils'

export function createWhiteboard(title: string, userIds: number[]) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/create`, {title, userIds})
}

export function deleteWhiteboard(socketId: string, whiteboardId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/delete?socketId=${socketId}`)
}

export function exportAsset(
  categoryIds: number[],
  description: string,
  title: string,
  whiteboardId: number,
) {
  const data = {
    categoryIds,
    description,
    title
  }
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/export/asset`, data)
}

export function getEligibleCollaborators() {
  return axios.get(`${utils.apiBaseUrl()}/api/whiteboards/eligible_collaborators`)
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

export function remixWhiteboard(assetId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/${assetId}/remix`, {assetId})
}

export function undelete(socketId: string, whiteboardId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/undelete`, {socketId})
}

export function updateWhiteboard(socketId: string, title: string, userIds: number[], whiteboardId: number) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/update`, {socketId, title, userIds})
}
