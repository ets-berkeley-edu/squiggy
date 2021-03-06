import axios from 'axios'
import utils from '@/api/api-utils'

export function getAllCanvasDomains() {
  return axios.get(`${utils.apiBaseUrl()}/api/canvas/all_domains`)
}
