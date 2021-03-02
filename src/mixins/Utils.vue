<script>
import _ from 'lodash'

export default {
  name: 'Utils',
  methods: {
    oxfordJoin: arr => {
      switch(arr.length) {
      case 1: return _.head(arr)
      case 2: return `${_.head(arr)} and ${_.last(arr)}`
      default: return _.join(_.concat(_.initial(arr), ` and ${_.last(arr)}`), ', ')
      }
    },
    stripAnchorRef: path => _.split(path, '#', 1)[0]
  }
}
</script>
