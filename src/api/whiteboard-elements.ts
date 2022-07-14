import axios from 'axios'
import utils from '@/api/api-utils'

export function createWhiteboard(title: string, userIds: number[]) {
  return axios.post(`${utils.apiBaseUrl()}/api/whiteboard/create`, {title, userIds})
}

export function deleteWhiteboardElement(socketId: string, uuid: string, whiteboardId: number) {
  return axios.delete(`${utils.apiBaseUrl()}/api/whiteboard/${whiteboardId}/element/${uuid}/delete?socketId=${socketId}`)
}
