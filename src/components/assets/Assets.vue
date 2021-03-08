<template>
  <div v-if="!loading">
    <div class="d-flex justify-space-between pt-2">
      <div class="w-50">
        <AssetsSearchForm :on-submit="search" />
      </div>
      <div>
        <v-btn
          elevation="2"
          large
          @click="go('/assets/manage')"
          @keypress.enter="go('/assets/manage')"
        >
          <span class="pr-2">
            <font-awesome-icon icon="cog" />
          </span>
          Manage Assets
        </v-btn>
      </div>
    </div>
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
import AssetsSearchForm from '@/components/assets/AssetsSearchForm'
import AssetUploadCard from '@/components/assets/AssetUploadCard'
import Context from '@/mixins/Context'
import InfiniteLoading from 'vue-infinite-loading'
import Utils from '@/mixins/Utils'
import {getAssets} from '@/api/assets'

export default {
  name: 'Assets',
  components: {AssetCard, AssetsSearchForm, AssetUploadCard, InfiniteLoading},
  mixins: [Context, Utils],
  data: () => ({
    assets: [],
    limit: 10,
    offset: 0,
    total: undefined
  }),
  created() {
    this.$loading()
    this.fetch().then(() => {
      this.$ready('Asset Library')
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
