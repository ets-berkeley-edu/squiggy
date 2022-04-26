<script>
import _ from 'lodash'
import constants from '@/store/whiteboarding/constants'
import Vue from 'vue'
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
      drawOptions: constants.DRAW_OPTIONS,
      shapeOptions: constants.SHAPE_OPTIONS,
      textSizeOptions: constants.TEXT_SIZE_OPTIONS
    }
  },
  computed: {
    ...mapGetters('whiteboarding', [
      'activeCanvasObject',
      'categories',
      'disableAll',
      'fitToScreen',
      'hideSidebar',
      'isModifyingElement',
      'isScrollingCanvas',
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
      'addAsset',
      'deleteActiveElements',
      'deleteWhiteboard',
      'init',
      'moveLayer',
      'onWhiteboardUpdate',
      'ping',
      'resetSelected',
      'setDisableAll',
      'setHideSidebar',
      'setMode',
      'updateSelected',
      'toggleZoom'
    ]),
    updateFreeDrawingBrush: properties => _.assignIn(Vue.prototype.$canvas.freeDrawingBrush, properties)
  }
}
</script>
