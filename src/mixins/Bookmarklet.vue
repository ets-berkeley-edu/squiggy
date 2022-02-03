<script>
import {mapActions, mapGetters} from 'vuex'
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'Bookmarklet',
  computed: {
    ...mapGetters('bookmarklet', [
      'categories',
      'selectedImages',
      'targetPage',
      'workflow'
    ])
  },
  methods: {
    ...mapActions('bookmarklet', [
      'init',
      'setSelectedImages',
      'setWorkflow'
    ]),
    closePopup() {
      this.$announcer.assertive('Canceled. Closing window.')
      getCasLogoutUrl().then(() => window.close())
    }
  }
}
</script>
