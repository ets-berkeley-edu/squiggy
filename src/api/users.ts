import axios from 'axios'
import utils from '@/api/api-utils'

export function getLeaderboard() {
  return axios.get(`${utils.apiBaseUrl()}/api/users/leaderboard`)
}

export function getUsers() {
  return axios.get(`${utils.apiBaseUrl()}/api/users`)
}

export function updateLookingForCollaborators(lookingForCollaborators) {
  return axios.post(`${utils.apiBaseUrl()}/api/users/me/looking_for_collaborators`, {lookingForCollaborators})
}

export function updatePersonalDescription(personalDescription) {
  return axios.post(`${utils.apiBaseUrl()}/api/users/me/personal_description`, {personalDescription})
}

export function updateSharePoints(share) {
  return axios.post(`${utils.apiBaseUrl()}/api/users/me/share`, {share})
}
