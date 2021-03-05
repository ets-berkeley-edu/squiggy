import axios from 'axios'
import utils from '@/api/api-utils'

export function getCategories() {
  return axios.get(`${utils.apiBaseUrl()}/api/categories`)
}
