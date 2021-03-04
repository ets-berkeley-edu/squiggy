import axios from 'axios'
import utils from '@/api/api-utils'
import Vue from 'vue'

export function devAuthLogIn(canvasApiDomain: string, canvasCourseId: string, uid: string, password: string) {
  return axios
      .post(`${utils.apiBaseUrl()}/api/auth/dev_auth_login`, {canvasApiDomain, canvasCourseId, password, uid})
        .then(data => {
          Vue.prototype.$currentUser = data
          return Vue.prototype.$currentUser
        }).catch(error => {
          return error
        })
}

export function getCasLogoutUrl() {
  return axios
      .post(`${utils.apiBaseUrl()}/api/auth/logout`)
      .then(data => {
          Vue.prototype.$currentUser = data
          return Vue.prototype.$currentUser
        })
}
