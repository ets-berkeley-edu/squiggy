<script>
import {mapActions, mapGetters} from 'vuex'
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'Bookmarklet',
  computed: {
    ...mapGetters('bookmarklet', [
      'images',
      'pageMetadata'
    ])
  },
  methods: {
    ...mapActions('bookmarklet', [
      'init'
    ]),
    closePopup() {
      this.$announcer.assertive('Canceled. Closing window.')
      getCasLogoutUrl().then(() => window.close())
    }
  }
}
</script>
