import axios from 'axios'
import utils from '@/api/api-utils'

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

export function remixWhiteboard(assetId: number, title: string) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/remix`, {assetId, title})
}
