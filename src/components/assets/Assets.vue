<template>
  <div v-if="!loading">
    <AssetsHeader
      :categories="categories"
      :on-submit="search"
      :users="users"
    />
    <v-card
      class="d-flex flex-wrap"
      flat
      tile
    >
      <AssetUploadCard />
      <AssetCard
        v-for="(asset, $index) in assets"
        :key="$index"
        :asset="asset"
        class="ma-3"
      />
    </v-card>
    <InfiniteLoading spinner="waveDots" @infinite="fetchMore" />
  </div>
</template>

<script>
import AssetCard from '@/components/assets/AssetCard'
import AssetsHeader from '@/components/assets/AssetsHeader'
import AssetUploadCard from '@/components/assets/AssetUploadCard'
import Context from '@/mixins/Context'
import InfiniteLoading from 'vue-infinite-loading'
import Utils from '@/mixins/Utils'
import {getAssets} from '@/api/assets'
import {getCategories} from '@/api/categories'
import {getUsers} from '@/api/users'

export default {
  name: 'Assets',
  components: {AssetCard, AssetsHeader, AssetUploadCard, InfiniteLoading},
  mixins: [Context, Utils],
  data: () => ({
    assets: [],
    categories: undefined,
    limit: 10,
    offset: 0,
    total: undefined,
    users: undefined
  }),
  created() {
    this.$loading()
    getUsers().then(data => {
      this.users = data
      getCategories().then(data => {
        this.categories = data
        this.fetch().then(() => {
          this.$ready('Asset Library')
        })
      })
    })
  },
  methods: {
    fetch() {
      return getAssets(
        this.$currentUser.course.canvasApiDomain,
        this.$currentUser.course.canvasCourseId,
        {
          limit: this.limit,
          offset: this.offset
        }
      ).then(data => {
        this.assets.unshift(...data.results.reverse())
        this.total = data.total
        this.offset += this.limit
        return data
      })
    },
    fetchMore($state) {
      this.fetch().then(data => data.results.length ? $state.loaded() : $state.complete())
    },
    search() {
      console.log('TODO: Search')
    }
  }
}
</script>
