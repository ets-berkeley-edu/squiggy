import axios from 'axios'
import utils from '@/api/api-utils'

export function getUsers() {
  return axios.get(`${utils.apiBaseUrl()}/api/users`)
}
