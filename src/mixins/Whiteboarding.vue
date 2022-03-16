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
      'whiteboard',
      'disableAll',
      'fabricElementTemplates',
      'isReadOnly',
      'unsavedFabricElement',
      'windowHeight',
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
