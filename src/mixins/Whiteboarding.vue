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
      'elementJsons',
      'windowHeight',
      'windowWidth'
    ])
  },
  methods: {
    ...mapActions('whiteboard', [
      'add',
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
