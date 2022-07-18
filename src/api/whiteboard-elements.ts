import axios from 'axios'
import utils from '@/api/api-utils'

export function deleteWhiteboardElement(socketId: string, uuid: string, whiteboardId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/element/${uuid}/delete?socketId=${socketId}`)
}

export function updateWhiteboardElementsOrder(socketId: string, uuids: string[], whiteboardId: number) {
  return axios.post(
    `${utils.apiBaseUrl()}/api/whiteboard_elements/order`,
    {socketId, uuids, whiteboardId}
  )
}

export function upsertWhiteboardElements(socketId: string, whiteboardElements: any[], whiteboardId: number) {
  return axios.post(
    `${utils.apiBaseUrl()}/api/whiteboard_elements/upsert`,
    {socketId, whiteboardElements, whiteboardId}
  )
}
