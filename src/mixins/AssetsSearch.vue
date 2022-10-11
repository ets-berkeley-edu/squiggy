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
      'groupId',
      'isDirty',
      'keywords',
      'limit',
      'orderBy',
      'orderByDefault',
      'sections',
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
      'initAssetSearchOptions',
      'nextPage',
      'resetSearch',
      'search',
      'setAssetType',
      'setCategoryId',
      'setGroupId',
      'setKeywords',
      'setOrderBy',
      'setSection',
      'setUserId',
      'updateAssetStore'
    ])
  }
}
</script>
