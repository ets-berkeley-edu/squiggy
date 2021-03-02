<script>
import {mapGetters} from 'vuex'

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', ['loading'])
  },
  methods: {
    alertScreenReader(message, politeness='polite') {
      this.$announcer.set(message, politeness)
    }
  }
}
</script>
