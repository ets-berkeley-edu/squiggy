<script>
import {mapGetters} from 'vuex'

export default {
  name: 'Context',
  computed: {
    ...mapGetters('context', ['loading'])
  }
}
</script>
