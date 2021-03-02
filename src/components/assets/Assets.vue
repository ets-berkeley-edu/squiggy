<template>
  <div v-if="!loading">
    <h1>{{ assets.results.length }} Assets</h1>
    <div>
      <v-card
        class="d-flex flex-wrap"
        flat
        tile
      >
        <v-card
          v-for="(asset, index) in assets.results"
          :key="index"
          class="pa-2"
          outlined
          tile
        >
          {{ asset.title }} by {{ oxfordJoin($_.map(asset.users, 'canvas_full_name')) }}
        </v-card>
      </v-card>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getAssets} from '@/api/assets'

export default {
  name: 'Assets',
  mixins: [Context, Utils],
  data: () => ({
    assets: undefined
  }),
  created() {
    this.$loading()
    getAssets('bcourses.berkeley.edu', 1502870).then(data => {
      this.assets = data
      this.$ready()
    })
  }
}
</script>
