import Vue from 'vue'
import utils from '@/utils'

const $_goToLogin = (to: any, next: any) => {
  next({
    path: '/login',
    query: {
      error: to.query.error,
      redirect: to.name === 'home' ? undefined : to.fullPath
    }
  })
}

export default {
  requiresAuthenticated: (to: any, from: any, next: any) => {
    const currentUser = Vue.prototype.$currentUser
    if (currentUser.isAuthenticated) {
      next()
    } else if (utils.isInIframe()) {
      next({
        path: '/error',
        query: {
          m: 'Sorry, you are not authorized to use this tool.'
        }
      })
    } else {
      $_goToLogin(to, next)
    }
  },
  requiresInstructor: (to: any, from: any, next: any) => {
    const currentUser = Vue.prototype.$currentUser
    if (currentUser.isTeaching || currentUser.isAdmin) {
      next()
    } else {
      $_goToLogin(to, next)
    }
  }
}
