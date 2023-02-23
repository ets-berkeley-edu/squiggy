import axios from 'axios'
import utils from '@/api/api-utils'

export function activate() {
  return axios.post(`${utils.apiBaseUrl()}/api/course/activate`)
}

export function getCourse(courseId) {
  return axios.get(`${utils.apiBaseUrl()}/api/course/${courseId}`)
}

export function isCurrentCourseActive() {
  return axios.get(`${utils.apiBaseUrl()}/api/course/is_active`)
}

export function updateProtectAssetsPerSectionCheckbox(protectSectionCheckbox) {
  return axios.post(`${utils.apiBaseUrl()}/api/course/update_protect_assets_per_section`,
      {protectSectionCheckbox})
}
