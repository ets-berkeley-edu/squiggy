<template>
  <div id="asset-library">
    <SyncDisabled v-if="$currentUser.isAdmin || $currentUser.isTeaching" />
    <AssetsHeader ref="header" />
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
import InfiniteLoading from '@/mixins/InfiniteLoading'
import SyncDisabled from '@/components/util/SyncDisabled'
import Utils from '@/mixins/Utils'

export default {
  name: 'Assets',
  components: {AssetCard, AssetsHeader, CreateAssetCard, SyncDisabled},
  mixins: [AssetsSearch, Context, InfiniteLoading, Utils],
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
          skeletonCount = this.totalAssetCount - this.assets.length
        }
        return this.assets.concat(this.getSkeletons(skeletonCount))
      }
    }
  },
  created() {
    this.$loading(true)
  },
  mounted() {
    this.anchor = this.$route.query.anchor
    this.isReturning = this.anchor && this.$_.size(this.assets)
    if (this.isReturning) {
      this.handleResults()
    } else {
      this.resetSearch()
      this.isComplete = false
      this.stopInfiniteLoading()
      this.getBookmarkHash().then(bookmarkHash => {
        if (bookmarkHash && Object.keys(bookmarkHash).length) {
          this.setAssetType(bookmarkHash.assetType)
          this.setCategoryId(bookmarkHash.categoryId)
          this.setOrderBy(bookmarkHash.orderBy)
          this.setUserId(parseInt(bookmarkHash.userId, 10))
          this.$announcer.polite('Searching for matching assets')
          this.search().then(data => {
            this.handleResults(data, true)
          })
        } else if (this.$route.query.userId) {
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
          this.search().then(this.handleResults)
        }
      })
    }
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
      if (this.$refs.header) {
        this.$refs.header.initialize()
      }

      let assetTotal = this.totalAssetCount
      if (data) {
        this.isComplete = !data.results.length
        assetTotal = data.total
      } else {
        this.isComplete = (this.assets.length === this.totalAssetCount)
      }

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

<style scoped>
.asset-card {
  height: 270px !important;
  width: 236px !important;
}
</style>
