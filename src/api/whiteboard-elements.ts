import axios from 'axios'
import utils from '@/api/api-utils'

export function deleteWhiteboardElement(socketId: string, uuids: string[], whiteboardId: number) {
  return axios.delete(
  `${utils.apiBaseUrl()}/api/whiteboard_elements/delete`,
    {
      data: {
        socketId,
        uuids,
        whiteboardId
      }
  })
}

export function updateWhiteboardElementsOrder(
    direction: string,
    socketId: string,
    uuids: string[],
    whiteboardId: number
) {
  return axios.post(
    `${utils.apiBaseUrl()}/api/whiteboard_elements/order`,
    {direction, socketId, uuids, whiteboardId}
  )
}

export function upsertWhiteboardElements(socketId: string, whiteboardElements: any[], whiteboardId: number) {
  return axios.post(
    `${utils.apiBaseUrl()}/api/whiteboard_elements/upsert`,
    {socketId, whiteboardElements, whiteboardId}
  )
}
