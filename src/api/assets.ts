import _ from 'lodash'
import axios from 'axios'
import utils from '@/api/api-utils'

export function getAssets(domain, courseSiteId, args={}) {
  let url = `${utils.apiBaseUrl()}/api/${domain}/${courseSiteId}/assets?`
  _.each(args, (value, key) => url += `${key}=${value}&`)
  return axios.get(url)
}

export function createLinkAsset(category, description, title, url) {
  return axios.post(`${utils.apiBaseUrl()}/api/auth/dev_auth_login`, {
    category,
    description,
    title,
    url
  })
}
