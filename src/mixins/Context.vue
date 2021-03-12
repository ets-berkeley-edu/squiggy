<script>
import {mapGetters} from 'vuex'

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', ['isLoading', 'noSpinnerWhenLoading'])
  }
}
</script>
