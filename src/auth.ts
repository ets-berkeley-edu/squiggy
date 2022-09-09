import Vue from 'vue'

export default {
  requiresAuthenticated: (to: any, from: any, next: any) => {
    const currentUser = Vue.prototype.$currentUser
    if (currentUser.isAuthenticated) {
      next()
    } else {
      next({
        path: '/error',
        query: {
          m: 'Sorry, you are not authorized to use this tool, or your ' +
              `<a href="${Vue.prototype.$config.browserKbUrl}" target="_blank">browser ` +
              'settings</a> do not support this tool.'
        }
      })
    }
  },
  requiresInstructor: (to: any, from: any, next: any) => {
    const currentUser = Vue.prototype.$currentUser
    if (currentUser.isTeaching || currentUser.isAdmin) {
      next()
    } else {
      next({
        path: '/error',
        query: {
          m: 'Sorry, you are not authorized to use this tool.'
        }
      })
    }
  }
}
