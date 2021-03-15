<template>
  <div id="asset-library">
    <AssetsHeader :categories="categories" :users="users" />
    <v-card class="d-flex flex-wrap" flat tile>
      <CreateAssetCard class="asset-card ma-3" />
      <AssetCard
        v-for="(asset, index) in (isLoading ? skeletons : assets)"
        :key="index"
        :asset="asset"
        class="asset-card ma-3"
      />
    </v-card>
    <InfiniteLoading v-if="!isLoading && (assets.length < totalAssetCount)" spinner="waveDots" @infinite="fetch" />
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
import {getCategories} from '@/api/categories'
import {getUsers} from '@/api/users'

export default {
  name: 'Assets',
  components: {AssetCard, AssetsHeader, CreateAssetCard, InfiniteLoading},
  mixins: [AssetsSearch, Context, Utils],
  data: () => ({
    categories: undefined,
    skeletons: Array.from(new Array(40), () => ({isLoading: true})),
    users: undefined
  }),
  created() {
    this.$loading(true)
    getUsers().then(data => {
      this.users = data
      getCategories().then(data => {
        this.categories = data
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
      })
    })
  },
  methods: {
    fetch($state) {
      this.nextPage().then(assets => assets.length ? $state.loaded() : $state.complete())
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
