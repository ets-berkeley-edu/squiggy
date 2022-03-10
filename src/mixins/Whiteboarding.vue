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
      'unsavedFabricElement',
      'windowHeight',
      'windowWidth'
    ]),
    canvas() {
      return this.$_.map(this.board.whiteboardElements, 'element').find(e => e.type === 'canvas')
    }
  },
  methods: {
    ...mapActions('whiteboarding', [
      'add',
      'getObjectAttribute',
      'init',
      'saveWhiteboardElements'
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
