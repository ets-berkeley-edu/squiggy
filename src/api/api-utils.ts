import _ from 'lodash'
import axios from 'axios'
import Vue from 'vue'

export default {
  apiBaseUrl: () => Vue.prototype.$config.apiBaseUrl,
  postMultipartFormData: (path: string, data: object) => {
    const formData = new FormData()
    _.forOwn(data, (value, key) => {
      if (!_.isNil(value)) {
        formData.append(key, value)
      }
    })
    return axios.post(
      path,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
  }
}
