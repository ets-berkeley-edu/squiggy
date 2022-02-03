<script>
import {mapActions, mapGetters} from 'vuex'
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'Bookmarklet',
  computed: {
    ...mapGetters('bookmarklet', [
      'categories',
      'images',
      'pageMetadata',
      'workflow'
    ])
  },
  methods: {
    ...mapActions('bookmarklet', [
      'init',
      'setWorkflow'
    ]),
    closePopup() {
      this.$announcer.assertive('Canceled. Closing window.')
      getCasLogoutUrl().then(() => window.close())
    }
  }
}
</script>
