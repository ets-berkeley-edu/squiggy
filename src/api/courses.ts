import axios from 'axios'
import utils from '@/api/api-utils'

export function activate() {
  return axios.post(`${utils.apiBaseUrl()}/api/course/activate`)
}
