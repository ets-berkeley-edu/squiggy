import axios from 'axios'
import utils from '@/api/api-utils'

export function updateAsset(assetId, categoryId, description, title) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/update`, {
    assetId,
    categoryId,
    description,
    title
  })
}

export function createLinkAsset(categoryId, description, title, url) {
  return axios.post(`${utils.apiBaseUrl()}/api/asset/create`, {
    categoryId,
    description,
    title,
    type: 'link',
    url
  })
}

export function deleteAsset(assetId) {
  return axios.delete(`${utils.apiBaseUrl()}/api/asset/${assetId}/delete`)
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

export function likeAsset(assetId) {
  return axios.get(`/api/asset/${assetId}/like`)
}

export function uploadFile(file) {
  return utils.postMultipartFormData('/api/asset/upload', {'file[0]': file})
}
