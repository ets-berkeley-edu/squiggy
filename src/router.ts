import _ from 'lodash'
import AddLinkAsset from '@/components/assets/AddLinkAsset.vue'
import Asset from '@/components/assets/Asset.vue'
import Assets from '@/components/assets/Assets.vue'
import AssetUpload from '@/components/assets/AssetUpload.vue'
import BaseView from '@/components/BaseView.vue'
import EditAsset from '@/components/assets/EditAsset.vue'
import Engage from '@/components/engage/Engage.vue'
import Error from '@/components/Error.vue'
import ManageAssets from '@/components/assets/ManageAssets.vue'
import NotFound from '@/components/NotFound.vue'
import Router from 'vue-router'
import utils from './utils'
import Squiggy from '@/components/Squiggy.vue'
import Vue from 'vue'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      redirect: '/squiggy'
    },
    {
      path: '/',
      component: BaseView,
      children: [
        {
          path: '/squiggy',
          component: Squiggy,
          meta: {
            isLoginPage: true,
            title: 'Hello!'
          }
        },
        {
          path: '/asset/create',
          component: AddLinkAsset,
          meta: {
            title: 'Add Link Asset'
          }
        },
        {
          path: '/asset/upload',
          component: AssetUpload,
          meta: {
            title: 'Upload Asset'
          }
        },
        {
          beforeEnter: (to: any, from: any, next: any) => {
            const assetId = utils.extractBookmarkId(to, 'asset')
            if (assetId) {
              next(`/asset/${assetId}`)
            } else {
              next()
            }
          },
          path: '/assets',
          component: Assets,
          meta: {
            title: 'Assets'
          }
        },
        {
          path: '/assets/manage',
          component: ManageAssets,
          meta: {
            title: 'Manage Assets'
          }
        },
        {
          path: '/asset/:id',
          component: Asset,
          meta: {
            title: 'Asset'
          }
        },
        {
          path: '/asset/:id/edit',
          component: EditAsset,
          meta: {
            title: 'Asset'
          }
        },
        {
          path: '/engage',
          component: Engage,
          meta: {
            title: 'Engagement Index'
          }
        }
      ]
    },
    {
      path: '/',
      component: BaseView,
      children: [
        {
          path: '/404',
          component: NotFound,
          meta: {
            title: 'Page not found'
          }
        },
        {
          path: '/error',
          component: Error,
          meta: {
            title: 'Error'
          }
        },
        {
          path: '*',
          redirect: '/404'
        }
      ]
    }
  ]
})

router.afterEach((to: any) => {
  const pageTitle = _.get(to, 'meta.title')
  document.title = `${pageTitle || _.capitalize(to.name) || 'Welcome'} | SuiteC`
  Vue.prototype.$announcer.assertive(`${pageTitle || 'Page'} is loading`)
})

export default router
