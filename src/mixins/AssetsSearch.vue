<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'AssetsSearch',
  computed: {
    ...mapGetters('assets', ['assets'])
  },
  methods: {
    ...mapActions('assets', ['nextPage', 'search'])
  }
}
</script>
