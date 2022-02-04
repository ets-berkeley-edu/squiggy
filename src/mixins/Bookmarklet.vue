<script>
import {mapActions, mapGetters} from 'vuex'
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'Bookmarklet',
  computed: {
    ...mapGetters('bookmarklet', [
      'categories',
      'course',
      'isAuthorized',
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
      this.$announcer.assertive('Popup window is closing.')
      getCasLogoutUrl().then(() => window.close())
    }
  }
}
</script>
