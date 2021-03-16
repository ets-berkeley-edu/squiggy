<script>
import {mapActions, mapGetters} from 'vuex'

export default {
  name: 'AssetsSearch',
  computed: {
    ...mapGetters('assets', [
      'assets',
      'assetType',
      'categoryId',
      'isDirty',
      'keywords',
      'limit',
      'orderBy',
      'orderByDefault',
      'totalAssetCount',
      'userId'
    ])
  },
  methods: {
    ...mapActions('assets', [
      'nextPage',
      'search',
      'setAssetType',
      'setCategoryId',
      'setKeywords',
      'setOrderBy',
      'setUserId'
    ])
  }
}
</script>
