import axios from 'axios'
import utils from '@/api/api-utils'

export function getLeaderboard() {
  return axios.get(`${utils.apiBaseUrl()}/api/users/leaderboard`)
}

export function getStudentsBySection() {
  return axios.get(`${utils.apiBaseUrl()}/api/users/students_by_section`)
}

export function getUsers() {
  return axios.get(`${utils.apiBaseUrl()}/api/users`)
}

export function updateSharePoints(share) {
  return axios.post(`${utils.apiBaseUrl()}/api/users/me/share`, {share})
}
