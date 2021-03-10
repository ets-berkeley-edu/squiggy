import _ from 'lodash'
import axios from 'axios'
import Vue from 'vue'

export default {
  apiBaseUrl: () => Vue.prototype.$config.apiBaseUrl,
  postMultipartFormData: (path: string, data: object) => {
    const formData = new FormData()
    _.each(data, (value, key) => !_.isNil(value) && formData.append(key, value))
    return axios.post(
      `${Vue.prototype.$config.apiBaseUrl}${path}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
  }
}
