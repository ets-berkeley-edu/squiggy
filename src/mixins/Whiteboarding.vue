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
      'elementJsons',
      'unsavedFabricElement',
      'windowHeight',
      'windowWidth'
    ]),
    canvas() {
      return this.elementJsons.find(e => e.type === 'canvas')
    },
    elementJsons() {
      return this.$_.map(this.board.elements, 'element')
    }
  },
  methods: {
    ...mapActions('whiteboarding', [
      'add',
      'getObjectAttribute',
      'init',
      'saveElement'
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
