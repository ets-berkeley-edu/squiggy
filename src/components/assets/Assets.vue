<template>
  <div id="asset-library">
    <SyncDisabled v-if="$currentUser.isAdmin || $currentUser.isTeaching" />
    <AssetsHeader ref="header" />
    <v-card class="d-flex flex-wrap" flat tile>
      <CreateAssetCard class="asset-card ma-3" />
      <AssetCard
        v-for="(asset, index) in infiniteScroll"
        :key="index"
        :asset="asset"
        class="asset-card ma-3"
      />
      <InfiniteLoading v-if="!isLoading || true" @infinite="fetch">
        <template #error>Sorry, an error occurred. Please refresh the page.</template>
        <template #no-more><span id="no-more-assets-to-fetch" /></template>
        <template #no-results><span id="zero-assets" /></template>
        <template #spinner><span class="sr-only">Loading...</span></template>
      </InfiniteLoading>
    </v-card>
  </div>
</template>

<script>
import AssetCard from '@/components/assets/AssetCard'
import AssetsHeader from '@/components/assets/AssetsHeader'
import AssetsSearch from '@/mixins/AssetsSearch'
import Context from '@/mixins/Context'
import CreateAssetCard from '@/components/assets/CreateAssetCard'
import InfiniteLoading from 'vue-infinite-loading'
import SyncDisabled from '@/components/util/SyncDisabled'
import Utils from '@/mixins/Utils'

export default {
  name: 'Assets',
  components: {AssetCard, AssetsHeader, CreateAssetCard, InfiniteLoading, SyncDisabled},
  mixins: [AssetsSearch, Context, Utils],
  data: () => ({
    anchor: null,
    isComplete: false
  }),
  computed: {
    infiniteScroll() {
      this.$nextTick(() => this.resizeIFrame)
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
      this.getBookmarkHash().then(bookmarkHash => {
        if (bookmarkHash && Object.keys(bookmarkHash).length) {
          this.setAssetType(bookmarkHash.assetType)
          this.setCategoryId(bookmarkHash.categoryId)
          this.setOrderBy(bookmarkHash.orderBy)
          this.setUserId(parseInt(bookmarkHash.userId, 10))
          this.search().then(this.handleResults)
        } else if (this.$route.query.userId) {
          this.setAssetType(undefined)
          this.setCategoryId(undefined)
          this.setUserId(parseInt(this.$route.query.userId, 10))
          this.$router.replace({query: {userId: undefined}})
          this.search().then(data => {
            this.updateSearchBookmark()
            this.handleResults(data)
          })
        } else if (this.$route.query.categoryId) {
          this.setAssetType(undefined)
          this.setCategoryId(parseInt(this.$route.query.categoryId, 10))
          this.setUserId(undefined)
          this.$router.replace({query: {categoryId: undefined}})
          this.search().then(data => {
            this.updateSearchBookmark()
            this.handleResults(data)
          })
        } else {
          this.search().then(this.handleResults)
        }
      })
    }
  },
  methods: {
    fetch($state) {
      this.nextPage().then(data => {
        if (data.results.length) {
          $state.loaded()
          this.$announcer.polite(`${this.assets.length} of ${this.totalAssetCount} assets loaded.`)
        } else {
          $state.complete()
          this.isComplete = true
          this.$announcer.polite(`All ${this.totalAssetCount} assets have loaded.`)
        }
      })
    },
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true})),
    handleResults(data) {
      if (this.$refs.header) {
        this.$refs.header.initialize()
      }
      this.$ready('Asset Library')
      if (data) {
        this.isComplete = !data.results.length
      }
      if (this.anchor) {
        this.scrollTo(`#${this.anchor}`)
        this.$putFocusNextTick(this.anchor)
      }
      const srAlert = `${this.isReturning ? 'Returning to Asset Library. ' : ''}${this.totalAssetCount} assets total.`
      this.$announcer.polite(srAlert)
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
