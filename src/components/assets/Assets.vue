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
        class="ma-3"
      >
        <v-sheet elevation="1">
          <v-img src="@/assets/mock-asset-preview.png">
            <v-card-text class="asset-metadata">
              <div>
                {{ asset.title }}
              </div>
              <div>
                by {{ oxfordJoin($_.map(asset.users, 'canvasFullName')) }}
              </div>
            </v-card-text>
          </v-img>
        </v-sheet>
        <v-card-actions>
          <div class="d-flex justify-space-between">
            <div>
              <button :id="`iconbar-pin-${asset.id}`">
                <v-icon>
                  mdi-pin
                  <span v-if="!asset.isPinnedByMe" class="sr-only">Pin</span>
                  <span v-if="asset.isPinnedByMe" class="sr-only">Pinned</span>
                </v-icon>
              </button>
            </div>
            <div>
              <v-btn :id="`iconbar-like-${asset.id}`">
                <v-icon>
                  mdi-thumb-up-outline
                  <span class="sr-only">Like</span>
                </v-icon>
              </v-btn>
              {{ asset.likes }}
              <v-icon>
                mdi-eye-outline
                <span class="sr-only">Views</span>
              </v-icon>
              {{ asset.views }}
              <v-icon>
                mdi-comment-outline
                <span class="sr-only">Comments</span>
              </v-icon>
              {{ asset.commentCount }}
            </div>
          </div>
        </v-card-actions>
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
    }
  }
}
</script>

<style scoped>
.asset-metadata {
  background-color: #333;
  background-color: rgba(51, 51, 51, 0.9);
  bottom: 0;
  color: #FFF;
  left: 0;
  position: absolute;
  right: 0;
}

.asset-metadata span {
  font-size: 14px;
  font-weight: 400;
  line-height: 1.3;
  margin-bottom: 5px;
  margin-top: 0;
}

.asset-metadata small {
  font-size: 13px;
}
</style>