import _ from 'lodash'
import Asset from '@/components/assets/Asset.vue'
import Assets from '@/components/assets/Assets.vue'
import auth from './auth'
import BaseView from '@/components/BaseView.vue'
import Engage from '@/components/engage/Engage.vue'
import Error from '@/components/Error.vue'
import ImpactStudio from '@/components/impactstudio/ImpactStudio.vue'
import LaunchFailure from '@/components/LaunchFailure.vue'
import ManageAssets from '@/components/assets/ManageAssets.vue'
import NotFound from '@/components/NotFound.vue'
import PointsConfiguration from '@/components/engage/PointsConfiguration.vue'
import Router from 'vue-router'
import Squiggy from '@/components/Squiggy.vue'
import store from '@/store'
import Vue from 'vue'
import Whiteboard from '@/components/whiteboards/Whiteboard.vue'
import Whiteboards from '@/components/whiteboards/Whiteboards.vue'

Vue.use(Router)

const router = new Router({
  mode: 'history',
  routes: [
    {
      beforeEnter: (to: any, from: any, next: any) => next(Vue.prototype.$config.isVueAppDebugMode ? '/squiggy' : '/404'),
      path: '/'
    },
    {
      path: '/',
      beforeEnter: auth.requiresAuthenticated,
      component: BaseView,
      children: [
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
                  next({
                    query: {
                      ...params,
                      ...(to.query || {})
                    }
                  })
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
        },
        {
          beforeEnter: (to: any, from: any, next: any) => {
            // Skip hash redirect if we're returning from an Impact Studio page.
            if (from.fullPath.match(/\/impact_studio\/\d+/)) {
              next()
            } else {
              store.dispatch('context/loadingStart')
              store.dispatch('context/getBookmarkHash').then(params => {
                if (params.userId) {
                  next(`/impact_studio/profile/${params.userId}`)
                } else {
                  next({
                    query: {
                      ...params,
                      ...(to.query || {})
                    }
                  })
                }
              })
            }
          },
          path: '/impact_studio',
          component: ImpactStudio,
          meta: {
            title: 'Impact Studio'
          }
        },
        {
          path: '/impact_studio/profile/:id',
          component: ImpactStudio,
          meta: {
            title: 'Impact Studio'
          }
        },
        {
          path: '/whiteboards',
          component: Whiteboards,
          meta: {
            title: 'Whiteboards'
          }
        }
      ]
    },
    {
      beforeEnter: auth.requiresAuthenticated,
      path: '/whiteboard/:id',
      component: Whiteboard,
      meta: {
        title: 'Whiteboard'
      }
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
          path: '/404',
          component: NotFound,
          meta: {
            hideStandaloneFooter: true,
            title: 'Page not found'
          }
        },
        {
          path: '/error',
          component: Error,
          meta: {
            hideStandaloneFooter: true,
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
