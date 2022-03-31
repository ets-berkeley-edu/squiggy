<script>
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
      'colors',
      'disableAll',
      'mode',
      'selected',
      'textSizeOptions',
      'windowHeight',
      'whiteboard',
      'windowWidth'
    ])
  },
  methods: {
    ...mapActions('whiteboarding', [
      'add',
      'deleteActiveElements',
      'getObjectAttribute',
      'getSelectedAssetParams',
      'init',
      'moveLayer',
      'saveWhiteboardElements',
      'setDisableAll',
      'setMode',
      'updateSelected',
      'toggleZoom'
    ])
  }
}
</script>
