<script>
import Context from '@/mixins/Context'
import {mapActions, mapGetters} from 'vuex'


export default {
  name: 'AssetsSearch',
  mixins: [Context],
  computed: {
    ...mapGetters('assets', [
      'assets',
      'assetType',
      'categories',
      'categoryId',
      'expanded',
      'isDirty',
      'keywords',
      'limit',
      'orderBy',
      'orderByDefault',
      'totalAssetCount',
      'userId',
      'users'
    ])
  },
  methods: {
    updateSearchBookmark() {
      this.rewriteBookmarkHash({
        assetType: this.assetType,
        categoryId: this.categoryId,
        keywords: this.keywords,
        orderBy: this.orderBy,
        userId: this.userId
      })
    },
    ...mapActions('assets', [
      'init',
      'nextPage',
      'resetSearch',
      'search',
      'setAssetType',
      'setCategoryId',
      'setExpanded',
      'setKeywords',
      'setOrderBy',
      'setUserId',
      'updateAssetStore'
    ])
  }
}
</script>
