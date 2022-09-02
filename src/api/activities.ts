import axios from 'axios'
import utils from '@/api/api-utils'

export function getCourseInteractions() {
  return axios.get(`${utils.apiBaseUrl()}/api/activities/interactions`)
}

export function getPointsConfiguration() {
  return axios.get(`${utils.apiBaseUrl()}/api/activities/configuration`)
}

export function getUserActivities(userId) {
  return axios.get(`${utils.apiBaseUrl()}/api/activities/user/${userId}`)
}

export function updatePointsConfiguration(activities) {
  return axios.post(`${utils.apiBaseUrl()}/api/activities/configuration`, activities)
}
