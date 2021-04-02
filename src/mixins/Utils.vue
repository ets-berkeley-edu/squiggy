<script>
import _ from 'lodash'
import VueScrollTo from 'vue-scrollto'

export default {
  name: 'Utils',
  data: () => ({
    rule: {
      isNumber: v => /^\s*\d+\s*$/.test(v) || 'Number required',
      notBlank: v => !!_.trim(v) || 'Required'
    }
  }),
  methods: {
    getApiErrorMessage: (data) => _.get(data, 'response.data.message') || data.message || _.get(data, 'response.statusText'),
    getPossessive(comment) {
      return comment.userId === this.$currentUser.id ? 'your' : `${comment.user.canvasFullName}'s`
    },
    go(path, query={}) {
      this.$router.push({path, query})
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
      this.$postIFrameMessage(() => ({
        // If Canvas instance supports custom messaging then send our custom 'changeParent' event (see above).
        height: document.body.offsetHeight,
        subject: this.$supportsCustomMessaging ? 'changeParent' : 'lti.frameResize'
      }))
    },
    scrollTo: (element, timeout=1000) => setTimeout(() => VueScrollTo.scrollTo(element), timeout),
    scrollToLtiTop: () => {
      window.scrollTo(0, 0)
      // If running as BasicLTI then we also scroll parent window to top.
      if (window.parent) {
        if (this.$supportsCustomMessaging) {
          // If hosting Canvas supports our custom 'changeParent' cross-window event then use it.
          this.$postIFrameMessage(() => ({subject: 'changeParent', scrollToTop: true}))
        } else {
          // Otherwise, use the standard Canvas event.
          this.$postIFrameMessage(() => ({subject: 'lti.scrollToTop'}))
        }
      }
    },
    setParentHash(params) {
      if (this.$supportsCustomMessaging) {
        this.$postIFrameMessage(() => ({
          subject: 'setParentHash',
          hash: _.map(params, (value, key) => `suitec_${key}=${encodeURIComponent(value)}`).join('&')
        }))
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
