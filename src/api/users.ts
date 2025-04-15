import axios from 'axios'
import utils from '@/api/api-utils'

export function getLeaderboard() {
  return axios.get(`${utils.apiBaseUrl()}/api/users/leaderboard`)
}

export function getUsers() {
  return axios.get(`${utils.apiBaseUrl()}/api/users`)
}
