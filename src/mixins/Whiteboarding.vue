<script>
import constants from '@/store/whiteboarding/constants'
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
  data() {
    return {
      colors: constants.COLORS,
      textSizeOptions: constants.TEXT_SIZE_OPTIONS
    }
  },
  computed: {
    ...mapGetters('whiteboarding', [
      'activeCanvasObject',
      'disableAll',
      'isModifyingElement',
      'mode',
      'selected',
      'selectedAsset',
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
      'resetSelected',
      'saveWhiteboardElements',
      'setDisableAll',
      'setMode',
      'updateSelected',
      'toggleZoom'
    ])
  }
}
</script>
