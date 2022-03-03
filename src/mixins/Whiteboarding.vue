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
      'whiteboard',
      'windowHeight',
      'windowWidth'
    ])
  },
  methods: {
    ...mapActions('whiteboard', [
      'init'
    ]),
    ...mapMutations('whiteboard', [
      'onWindowResize'
    ])
  }
}
</script>
