<template>
  <div id="asset-library">
    <AssetsHeader />
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
import Utils from '@/mixins/Utils'

export default {
  name: 'Assets',
  components: {AssetCard, AssetsHeader, CreateAssetCard, InfiniteLoading},
  mixins: [AssetsSearch, Context, Utils],
  data: () => ({
    isComplete: false
  }),
  computed: {
    infiniteScroll() {
      return this.isLoading ? this.getSkeletons(20) : (this.isComplete ? this.assets : this.assets.concat(this.getSkeletons(10)))
    }
  },
  created() {
    this.$loading(true)
    const anchor = this.$route.query.anchor
    const isReturning = anchor && this.$_.size(this.assets)
    const ready = () => {
      this.$ready('Asset Library')
      if (anchor) {
        this.scrollTo(`#${anchor}`)
        this.$putFocusNextTick(anchor)
      }
      const srAlert = `${isReturning ? 'Returning to Asset Library. ' : ''}${this.totalAssetCount} assets total.`
      this.$announcer.polite(srAlert)
    }
    if (isReturning) {
      ready()
    } else {
      this.search().then(ready)
    }
  },
  methods: {
    fetch($state) {
      this.nextPage().then(assets => {
        if (assets.results.length) {
          $state.loaded()
          this.$announcer.polite(`${this.assets.length} of ${this.totalAssetCount} assets loaded.`)
        } else {
          $state.complete()
          this.isComplete = true
          this.$announcer.polite(`All ${this.totalAssetCount} assets have loaded.`)
        }
      })
    },
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true}))
  }
}
</script>

<style scoped>
.asset-card {
  height: 270px !important;
  width: 236px !important;
}
</style>
