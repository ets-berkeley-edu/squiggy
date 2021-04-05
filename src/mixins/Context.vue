<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', [
      'isInIframe',
      'isLoading',
      'noSpinnerWhenLoading'
    ])
  },
  methods: {
    ...mapActions('context', [
      'clearBookmarkHash',
      'getBookmarkHash',
      'rewriteBookmarkHash'
    ])
  }
}
</script>
