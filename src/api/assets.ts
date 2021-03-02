import axios from 'axios'
import utils from '@/api/api-utils'

export function getAssets(domain, courseSiteId) {
  return axios.get(`${utils.apiBaseUrl()}/api/${domain}/${courseSiteId}/assets`)
}
