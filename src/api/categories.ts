import axios from 'axios'
import utils from '@/api/api-utils'

export function createCategory(title) {
  return axios.post(`${utils.apiBaseUrl()}/api/category/create`, {title})
}

export function getCategories() {
  return axios.get(`${utils.apiBaseUrl()}/api/categories`)
}
