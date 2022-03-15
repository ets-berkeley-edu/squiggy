<script>
import {mapActions, mapMutations, mapGetters} from 'vuex'

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
