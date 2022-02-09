import _ from 'lodash'
import AddLinkAsset from '@/components/assets/AddLinkAsset.vue'
import Asset from '@/components/assets/Asset.vue'
import Assets from '@/components/assets/Assets.vue'
import AssetUpload from '@/components/assets/AssetUpload.vue'
import auth from './auth'
import BasePopupView from '@/components/BasePopupView.vue'
import BaseView from '@/components/BaseView.vue'
import BookmarkletPopup1 from '@/components/bookmarklet/BookmarkletPopup1.vue'
import BookmarkletPopup2 from '@/components/bookmarklet/BookmarkletPopup2.vue'
import BookmarkletPopup3 from '@/components/bookmarklet/BookmarkletPopup3.vue'
import BookmarkletPopup4 from '@/components/bookmarklet/BookmarkletPopup4.vue'
import BookmarkletPopup5 from '@/components/bookmarklet/BookmarkletPopup5.vue'
import BookmarkletStep1 from '@/components/bookmarklet/BookmarkletStep1.vue'
import BookmarkletStep2 from '@/components/bookmarklet/BookmarkletStep2.vue'
import BookmarkletStep3 from '@/components/bookmarklet/BookmarkletStep3.vue'
import BookmarkletStep4 from '@/components/bookmarklet/BookmarkletStep4.vue'
import EditAsset from '@/components/assets/EditAsset.vue'
import Engage from '@/components/engage/Engage.vue'
import Error from '@/components/Error.vue'
import LaunchFailure from '@/components/LaunchFailure.vue'
import ManageAssets from '@/components/assets/ManageAssets.vue'
import NotFound from '@/components/NotFound.vue'
import PointsConfiguration from '@/components/engage/PointsConfiguration.vue'
import Router from 'vue-router'
import Squiggy from '@/components/Squiggy.vue'
import store from '@/store'
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
          beforeEnter: (to: any, from: any, next: any) => Vue.prototype.$isBookmarklet ? next('/bookmarklet/error') : next(),
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
            // Skip hash redirect if we're returning from an asset page.
            if (from.fullPath.match(/\/asset\/\d+/)) {
              next()
            } else {
              store.dispatch('context/loadingStart')
              store.dispatch('context/getBookmarkHash').then(params => {
                if (params.assetId) {
                  next(`/asset/${params.assetId}`)
                } else {
                  next()
                }
              })
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
          beforeEnter: auth.requiresInstructor,
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
          path: '/bookmarklet/start',
          component: BookmarkletStep1,
          meta: {
            title: 'Bookmarklet'
          }
        },
        {
          path: '/bookmarklet/step2',
          component: BookmarkletStep2,
          meta: {
            title: 'Bookmarklet'
          }
        },
        {
          path: '/bookmarklet/step3',
          component: BookmarkletStep3,
          meta: {
            title: 'Bookmarklet'
          }
        },
        {
          path: '/bookmarklet/step4',
          component: BookmarkletStep4,
          meta: {
            title: 'Bookmarklet'
          }
        },
        {
          path: '/engage',
          component: Engage,
          meta: {
            title: 'Engagement Index'
          }
        },
        {
          path: '/engage/points',
          component: PointsConfiguration,
          meta: {
            title: 'Points Configuration'
          }
        }
      ]
    },
    {
      path: '/',
      component: BasePopupView,
      children: [
        {
          path: '/bookmarklet/popup/1',
          component: BookmarkletPopup1,
          meta: {
            title: 'Bookmarklet'
          }
        },
        {
          path: '/bookmarklet/popup/2',
          component: BookmarkletPopup2,
          meta: {
            title: 'Bookmarklet'
          }
        },
        {
          path: '/bookmarklet/popup/3',
          component: BookmarkletPopup3,
          meta: {
            title: 'Bookmarklet'
          }
        },
        {
          path: '/bookmarklet/popup/4',
          component: BookmarkletPopup4,
          meta: {
            title: 'Bookmarklet'
          }
        },
        {
          path: '/bookmarklet/popup/5',
          component: BookmarkletPopup5,
          meta: {
            title: 'Bookmarklet'
          }
        },
        {
          path: '/bookmarklet/error',
          component: Error,
          meta: {
            title: 'Bookmarklet Error'
          }
        },
        {
          path: '/bookmarklet/404',
          component: NotFound,
          meta: {
            title: 'Page not found'
          }
        }
      ]
    },
    {
      path: '/',
      component: BaseView,
      children: [
        {
          beforeEnter: (to: any, from: any, next: any) => Vue.prototype.$isBookmarklet ? next('/bookmarklet/404') : next(),
          path: '/404',
          component: NotFound,
          meta: {
            title: 'Page not found'
          }
        },
        {
          beforeEnter: (to: any, from: any, next: any) => Vue.prototype.$isBookmarklet ? next('/bookmarklet/error') : next(),
          path: '/error',
          component: Error,
          meta: {
            title: 'Error'
          }
        },
        {
          path: '/launchfailure',
          component: LaunchFailure,
          meta: {
            title: 'Launch Failure'
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
