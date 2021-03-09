<template>
  <div v-if="!loading">
    <AssetsHeader :categories="categories" :users="users" />
    <v-card class="d-flex flex-wrap" flat tile>
      <AssetUploadCard />
      <AssetCard
        v-for="(asset, $index) in assets"
        :key="$index"
        :asset="asset"
        class="ma-3"
      />
    </v-card>
    <InfiniteLoading spinner="waveDots" @infinite="fetch" />
  </div>
</template>

<script>
import AssetCard from '@/components/assets/AssetCard'
import AssetsHeader from '@/components/assets/AssetsHeader'
import AssetsSearch from '@/mixins/AssetsSearch'
import AssetUploadCard from '@/components/assets/AssetUploadCard'
import Context from '@/mixins/Context'
import InfiniteLoading from 'vue-infinite-loading'
import Utils from '@/mixins/Utils'
import {getCategories} from '@/api/categories'
import {getUsers} from '@/api/users'

export default {
  name: 'Assets',
  components: {AssetCard, AssetsHeader, AssetUploadCard, InfiniteLoading},
  mixins: [AssetsSearch, Context, Utils],
  data: () => ({
    categories: undefined,
    users: undefined
  }),
  created() {
    this.$loading()
    getUsers().then(data => {
      this.users = data
      getCategories().then(data => {
        this.categories = data
        this.search({}).then(() => {
          this.$ready('Asset Library')
        })
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
