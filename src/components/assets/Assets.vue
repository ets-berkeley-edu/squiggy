<template>
  <div v-if="!loading">
    <h1>Showing {{ assets.length }} of {{ total }} Assets</h1>
    <v-card
      class="d-flex flex-wrap"
      flat
      tile
    >
      <v-card
        v-for="(asset, $index) in assets"
        :key="$index"
        outlined
      >
        <v-sheet
          elevation="1"
          height="200"
          width="200"
        >
          <div>
            {{ $index + 1 }}. {{ asset.title }} by {{ oxfordJoin($_.map(asset.users, 'canvas_full_name')) }}
          </div>
          <div>
            id: {{ asset.id }}
          </div>
        </v-sheet>
      </v-card>
    </v-card>
    <InfiniteLoading spinner="waveDots" @infinite="fetchMore" />
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import InfiniteLoading from 'vue-infinite-loading'
import Utils from '@/mixins/Utils'
import {getAssets} from '@/api/assets'

export default {
  name: 'Assets',
  components: {InfiniteLoading},
  mixins: [Context, Utils],
  data: () => ({
    assets: [],
    limit: 10,
    offset: 0,
    total: undefined
  }),
  created() {
    this.$loading()
    this.fetch().then(this.$ready)
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
    }
  }
}
</script>
