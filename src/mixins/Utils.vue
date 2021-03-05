<script>
import _ from 'lodash'

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
    go(path) {
      this.$router.push({path}, _.noop)
    },
    oxfordJoin: arr => {
      switch(arr.length) {
      case 1: return _.head(arr)
      case 2: return `${_.head(arr)} and ${_.last(arr)}`
      default: return _.join(_.concat(_.initial(arr), ` and ${_.last(arr)}`), ', ')
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
