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
    ...mapGetters('whiteboard', [
      'board',
      'disableAll',
      'windowHeight',
      'windowWidth'
    ])
  },
  methods: {
    ...mapActions('whiteboard', [
      'addEllipsis',
      'addText',
      'getObjectAttribute',
      'init'
    ]),
    ...mapMutations('whiteboard', [
      'onWindowResize',
      'setDisableAll',
      'setObjectAttribute',
    ])
  }
}
</script>
