<script>
import _ from 'lodash'
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'Whiteboarding',
  mounted() {
    this.$nextTick(() => {
      window.addEventListener('resize', this.onWindowResize)
    })
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onWindowResize)
  },
  computed: {
    ...mapGetters('whiteboarding', [
      'activeCanvasObject',
      'categories',
      'disableAll',
      'isFitToScreen',
      'isModifyingElement',
      'isScrollingCanvas',
      'mode',
      'selected',
      'selectedAsset',
      'whiteboard'
    ]),
    usersOffline() {
      return _.filter(this.whiteboard.users, user => !user.isOnline)
    },
    usersOnline() {
      return _.filter(this.whiteboard.users, user => user.isOnline)
    }
  },
  methods: {
    ...mapActions('whiteboarding', [
      'init',
      'onWhiteboardUpdate',
      'refreshWhiteboard',
      'resetSelected',
      'setDisableAll',
      'setMode',
      'toggleFitToScreen',
      'updateSelected',
      'zoomIn',
      'zoomOut'
    ])
  }
}
</script>
