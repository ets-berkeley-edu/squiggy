<script>
import _ from 'lodash'
import Vue from 'vue'
import VueScrollTo from 'vue-scrollto'
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'Utils',
  data: () => ({
    rule: {
      isNumber: v => /^\s*\d+\s*$/.test(v) || 'Number required',
      notBlank: v => !!_.trim(v) || 'Required'
    }
  }),
  computed: {
    ...mapGetters('context', [
      'isInIframe'
    ])
  },
  methods: {
    ...mapActions('context', [
      'postIFrameMessage'
    ]),
    consoleLog(statement, force=false) {
      const isProduction = Vue.prototype.$config.isProduction
      if (!isProduction || force) {
        console.log(`🪲 ${statement}`)
      }
    },
    getApiErrorMessage: (data) => _.get(data, 'response.data.message') || data.message || _.get(data, 'response.statusText'),
    getPossessive(comment) {
      return comment.userId === this.$currentUser.id ? 'your' : `${comment.user.canvasFullName}'s`
    },
    getScrollInformation() {
      return new Promise(resolve => {
        if (this.isInIframe && Vue.prototype.$supportsCustomMessaging) {
          this.postIFrameMessage({
            generator: () => ({subject: 'getScrollInformation'}),
            callback: resolve
          })
        } else {
          resolve()
        }
      })
    },
    go(path, query={}) {
      this.$router.push({path, query})
    },
    isValidURL: (url) => {
      const pattern = new RegExp('^(https?:\\/\\/)?'+ // protocol
        '((([a-z\\d]([a-z\\d-]*[a-z\\d])*)\\.)+[a-z]{2,}|'+ // domain name
        '((\\d{1,3}\\.){3}\\d{1,3}))'+ // OR ip (v4) address
        '(\\:\\d+)?(\\/[-a-z\\d%_.~+]*)*'+ // port and path
        '(\\?[;&a-z\\d%_.~+=-]*)?'+ // query string
        '(\\#[-a-z\\d_]*)?$','i') // fragment locator
      return !!pattern.test(url)
    },
    oxfordJoin: arr => {
      switch(_.size(arr)) {
      case 0: return ''
      case 1: return _.head(arr)
      case 2: return `${_.head(arr)} and ${_.last(arr)}`
      default: return _.join(_.concat(_.initial(arr), ` and ${_.last(arr)}`), ', ')
      }
    },
    pluralize: (noun, count, substitutions={}, pluralSuffix='s') => {
      return (`${substitutions[count] || substitutions['other'] || count} ` + (count === 1 ? noun : `${noun}${pluralSuffix}`))
    },
    resizeIFrame() {
      if (this.isInIframe) {
        // If Canvas instance supports custom messaging then send our custom 'changeParent' event.
        const generator = () => ({
          height: document.body.offsetHeight,
          subject: this.$supportsCustomMessaging ? 'changeParent' : 'lti.frameResize'
        })
        this.postIFrameMessage({generator, callback: _.noop})
      }
    },
    scrollTo: (element, timeout=1000) => setTimeout(() => VueScrollTo.scrollTo(element), timeout),
    scrollToLtiTop: () => {
      window.scrollTo(0, 0)
      // If running as BasicLTI then we also scroll parent window to top.
      if (this.isInIframe) {
        if (this.$supportsCustomMessaging) {
          // If hosting Canvas supports our custom 'changeParent' cross-window event then use it.
          const generator = () => ({subject: 'changeParent', scrollToTop: true})
          this.postIFrameMessage({generator, callback: _.noop})
        } else {
          // Otherwise, use the standard Canvas event.
          const generator = () => ({subject: 'lti.scrollToTop'})
          this.postIFrameMessage({generator, callback: _.noop})
        }
      }
    },
    setColorScheme() {
      if (!this.isInIframe) {
        const mq = window.matchMedia('(prefers-color-scheme: dark)')
        this.$vuetify.theme.dark = mq.matches
        if (typeof mq.addEventListener === 'function') {
          mq.addEventListener('change', e => this.$vuetify.theme.dark = e.matches)
        }
      }
    },
    stripAnchorRef: path => _.split(path, '#', 1)[0],
    validate: (errors, rules, value, messageIfError=null) => {
      // Logic of 'rules' is governed by Vuetify framework: https://vuetifyjs.com/en/components/forms/#rules
      _.each(rules, rule => {
        let error = rule(value)
        if (error instanceof String) {
          errors.push(messageIfError || error)
          return false
        }
      })
    }
  }
}
</script>
