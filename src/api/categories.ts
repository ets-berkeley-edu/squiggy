import axios from 'axios'
import utils from '@/api/api-utils'

export function getCategories(domain, courseSiteId) {
  return axios.get(`${utils.apiBaseUrl()}/api/${domain}/${courseSiteId}/categories`)
}
