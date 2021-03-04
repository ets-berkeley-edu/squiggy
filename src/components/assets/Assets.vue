<template>
  <div v-if="!loading">
    <div class="d-flex justify-space-between pt-2">
      <div class="w-50">
        <v-text-field
          v-model="keywords"
          class="mb-0"
          clearable
          label="Search"
          solo
          type="search"
          @click:append-outer="search"
        >
          <template #append>
            <div class="ml-2">
              <font-awesome-icon icon="caret-down" />
            </div>
          </template>
          <template #append-outer>
            <div class="ml-2 mt-1">
              <font-awesome-icon icon="search" />
            </div>
          </template>
        </v-text-field>
      </div>
      <div>
        <v-btn
          elevation="2"
          large
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
import AssetUploadCard from '@/components/assets/AssetUploadCard'
import Context from '@/mixins/Context'
import InfiniteLoading from 'vue-infinite-loading'
import Utils from '@/mixins/Utils'
import {getAssets} from '@/api/assets'

export default {
  name: 'Assets',
  components: {AssetCard, AssetUploadCard, InfiniteLoading},
  mixins: [Context, Utils],
  data: () => ({
    assets: [],
    keywords: undefined,
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
        'bcourses.berkeley.edu',
        1502870,
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
