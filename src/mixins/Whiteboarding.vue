<script>
import store from '@/store'
import whiteboarding from '@/store/whiteboarding/index'
import {mapActions, mapMutations, mapGetters} from 'vuex'

export default {
  name: 'Whiteboarding',
  mounted() {
    store.registerModule('whiteboarding', whiteboarding)
    this.$nextTick(() => {
      window.addEventListener('resize', this.onWindowResize)
    })
  },
  beforeDestroy() {
    store.unregisterModule('whiteboarding')
    window.removeEventListener('resize', this.onWindowResize)
  },
  computed: {
    ...mapGetters('whiteboarding', [
      'board',
      'disableAll',
      'fabricElementTemplates',
      'isReadOnly',
      'unsavedFabricElement',
      'windowHeight',
      'windowWidth'
    ]),
    canvas() {
      return this.$_.find(this.$_.map(this.board.whiteboardElements, we => we['element']), e => e.type === 'canvas')
    }
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
      'toggleZoom'
    ]),
    ...mapMutations('whiteboarding', [
      'onWindowResize',
      'setDisableAll',
      'setUnsavedFabricElement',
      'updateUnsavedFabricElement'
    ])
  }
}
</script>
