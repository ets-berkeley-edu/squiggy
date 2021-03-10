import axios from 'axios'
import utils from '@/api/api-utils'

export function createLinkAsset(categoryIds, description, title, url) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/create`, {
    categoryIds,
    description,
    title,
    type: 'link',
    url
  })
}

export function getAsset(assetId) {
  return axios.get(`${utils.apiBaseUrl()}/api/asset/${assetId}`)
}

export function getAssets(
  assetType,
  categoryId,
  hasComments,
  hasLikes,
  hasViews,
  keywords,
  limit,
  offset,
  orderBy,
  sectionId,
  userId
) {
  return axios.post(
    `${utils.apiBaseUrl()}/api/assets`,
    {
      assetType,
      categoryId,
      hasComments,
      hasLikes,
      hasViews,
      keywords,
      limit,
      offset,
      orderBy,
      sectionId,
      userId
    }
  )
}

export function uploadFile(file) {
  return utils.postMultipartFormData('/api/asset/upload', {'file[0]': file})
}