import axios from 'axios'
import utils from '@/api/api-utils'

export function createCategory(title) {
  return axios.post(`${utils.apiBaseUrl()}/api/category/create`, {title})
}

export function deleteCategory(categoryId) {
  return axios.delete(`${utils.apiBaseUrl()}/api/category/${categoryId}/delete`)
}

export function getCategories(includeHidden) {
  return axios.get(`${utils.apiBaseUrl()}/api/categories?includeHidden=${includeHidden}`)
}

export function updateCategory(categoryId, title, visible?) {
  return axios.post(`${utils.apiBaseUrl()}/api/category/update`, {
    categoryId,
    title,
    visible
  })
}
