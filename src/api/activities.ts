import axios from 'axios'
import utils from '@/api/api-utils'

export function getPointsConfiguration() {
  return axios.get(`${utils.apiBaseUrl()}/api/activities/configuration`)
}

export function updatePointsConfiguration(activities) {
  return axios.post(`${utils.apiBaseUrl()}/api/activities/configuration`, activities)
}
