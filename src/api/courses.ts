import axios from 'axios'
import utils from '@/api/api-utils'

export function activate() {
  return axios.post(`${utils.apiBaseUrl()}/api/course/activate`)
}

export function getCourse(courseId) {
  return axios.get(`${utils.apiBaseUrl()}/api/course/${courseId}`)
}
