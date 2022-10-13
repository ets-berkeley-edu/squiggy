<template>
  <div id="asset-library">
    <SyncDisabled v-if="$currentUser.isAdmin || $currentUser.isTeaching" />
    <AssetsHeader
      ref="header"
      :open-advanced-search="openAdvancedSearch"
      :put-focus-on-load="anchor ? null : 'basic-search-input'"
    />
    <v-card class="d-flex flex-wrap" flat tile>
      <CreateAssetCard class="asset-card ma-3" />
      <AssetCard
        v-for="(asset, index) in assetGrid"
        :key="index"
        :asset="asset"
        class="asset-card ma-3"
      />
    </v-card>
  </div>
</template>

<script>
import AssetCard from '@/components/assets/AssetCard'
import AssetsHeader from '@/components/assets/AssetsHeader'
import AssetsSearch from '@/mixins/AssetsSearch'
import Context from '@/mixins/Context'
import CreateAssetCard from '@/components/assets/CreateAssetCard'
import InfiniteScrolling from '@/mixins/InfiniteScrolling'
import SyncDisabled from '@/components/util/SyncDisabled'
import Utils from '@/mixins/Utils'

export default {
  name: 'Assets',
  components: {AssetCard, AssetsHeader, CreateAssetCard, SyncDisabled},
  mixins: [AssetsSearch, Context, InfiniteScrolling, Utils],
  data: () => ({
    anchor: null,
    isComplete: false
  }),
  computed: {
    assetGrid() {
      this.$nextTick(this.resizeIFrame)
      if (this.isLoading) {
        return this.getSkeletons(20)
      } else if (this.isComplete) {
        return this.assets
      } else {
        let skeletonCount = 10
        if (this.totalAssetCount && (this.totalAssetCount - this.assets.length) < skeletonCount) {
          skeletonCount = Math.max(0, this.totalAssetCount - this.assets.length)
        }
        return this.assets.concat(this.getSkeletons(skeletonCount))
      }
    },
    openAdvancedSearch() {
      return !!(this.assetType || this.categoryId || (this.orderBy !== this.orderByDefault) || this.userId)
    }
  },
  created() {
    this.$loading(true)
  },
  mounted() {
    this.initAssetSearchOptions().then(() => {
      this.anchor = this.$route.query.anchor
      this.isReturning = this.anchor && this.$_.size(this.assets)
      if (this.isReturning) {
        this.consoleLog('Back to Asset Library')
        this.handleResults()
      } else {
        this.resetSearch()
        this.isComplete = false
        this.stopInfiniteLoading()
        this.getBookmarkHash().then(bookmarkHash => {
          if (bookmarkHash && Object.keys(bookmarkHash).length) {
            this.consoleLog(`Bookmark-hash for /assets: ${JSON.stringify(bookmarkHash)}`)
            this.setAssetType(bookmarkHash.assetType)
            this.setCategoryId(bookmarkHash.categoryId)
            this.setKeywords(bookmarkHash.keywords)
            this.setOrderBy(bookmarkHash.orderBy)
            this.setUserId(parseInt(bookmarkHash.userId, 10))
            this.$announcer.polite('Searching for matching assets')
            this.search().then(data => {
              this.handleResults(data, true)
            })
          } else if (this.$route.query.userId) {
            this.consoleLog(`/assets route.query.userId: ${this.$route.query.userId}`)
            this.setAssetType(undefined)
            this.setCategoryId(undefined)
            this.setUserId(parseInt(this.$route.query.userId, 10))
            this.$router.replace({query: {userId: undefined}})
            this.$announcer.polite('Searching for assets by user')
            this.search().then(data => {
              this.updateSearchBookmark()
              this.handleResults(data, true)
            })
          } else if (this.$route.query.categoryId) {
            this.consoleLog(`/assets route.query.categoryId: ${this.$route.query.categoryId}`)
            this.setAssetType(undefined)
            this.setCategoryId(parseInt(this.$route.query.categoryId, 10))
            this.setUserId(undefined)
            this.$router.replace({query: {categoryId: undefined}})
            this.$announcer.polite('Searching for assets by category')
            this.search().then(data => {
              this.updateSearchBookmark()
              this.handleResults(data, true)
            })
          } else {
            this.consoleLog('/assets: Default search')
            this.search().then(this.handleResults)
          }
        })
      }
    })
  },
  methods: {
    fetch() {
      return this.nextPage().then(data => {
        if (data.results.length) {
          this.$announcer.polite(`${this.assets.length} of ${this.totalAssetCount} assets loaded.`)
        } else {
          this.isComplete = true
          this.$announcer.polite(`All ${this.totalAssetCount} assets have loaded.`)
        }
      })
    },
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true})),
    handleResults(data, isSearching) {
      const assetTotal = data ? data.total : this.totalAssetCount
      this.isComplete = data ? !data.results.length : (this.assets.length === this.totalAssetCount)

      let announcement = null
      if (this.isReturning) {
        announcement = 'Returning to Asset Library'
      } else if (isSearching) {
        announcement = `${assetTotal} matching ${assetTotal === 1 ? 'asset' : 'assets'} found`
      }
      this.$ready('Asset Library', null, announcement)

      if (!this.isComplete) {
        this.startInfiniteLoading(this.fetch, {threshold: 800})
      }
      if (this.anchor) {
        this.scrollTo(`#${this.anchor}`)
        this.$putFocusNextTick(this.anchor)
      }
    }
  }
}
</script>
