import axios from 'axios'
import utils from '@/api/api-utils'

export function getLeaderboard() {
  return axios.get(`${utils.apiBaseUrl()}/api/users/leaderboard`)
}

export function getStudents() {
  return axios.get(`${utils.apiBaseUrl()}/api/users/students`)
}

export function getUsers() {
  return axios.get(`${utils.apiBaseUrl()}/api/users`)
}

export function updateSharePoints(share) {
  return axios.post(`${utils.apiBaseUrl()}/api/users/me/share`, {share})
}
