import axios from 'axios'
import utils from '@/api/api-utils'

export function getAdvancedAssetSearchOptions(courseId) {
  return axios.get(`${utils.apiBaseUrl()}/api/course/${courseId}/advanced_asset_search_options`)
}

export function getCourse(courseId) {
  return axios.get(`${utils.apiBaseUrl()}/api/course/${courseId}`)
}
