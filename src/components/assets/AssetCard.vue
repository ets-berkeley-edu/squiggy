<template>
  <kinesis-container>
    <kinesis-element :strength="10" type="depth">
      <v-skeleton-loader
        v-if="asset.isLoading"
        class="elevation-1 mx-auto"
        height="270"
        max-height="270"
        max-width="240"
        :tile="true"
        type="image, actions"
        width="240"
      />
      <v-card
        v-if="!asset.isLoading"
        :id="`asset-${asset.id}`"
        class="h-100"
        @click="go(`/asset/${asset.id}`)"
      >
        <v-sheet elevation="1">
          <v-img class="thumbnail" :src="thumbnailUrl" @error="imgError">
            <v-card-text class="asset-metadata">
              <div class="mb-3">
                {{ asset.title }}
              </div>
              <div>
                by {{ oxfordJoin($_.map(asset.users, 'canvasFullName')) }}
              </div>
            </v-card-text>
          </v-img>
        </v-sheet>
        <v-card-actions class="actions">
          <div class="d-flex justify-end w-100">
            <div>
              <div class="align-center d-flex">
                <div class="pr-3">
                  <font-awesome-icon icon="thumbs-up" />
                  {{ asset.likes }}
                </div>
                <div class="pr-3">
                  <font-awesome-icon icon="eye" />
                  {{ asset.views }}
                </div>
                <div>
                  <font-awesome-icon icon="comment" />
                  {{ asset.commentCount }}
                </div>
              </div>
            </div>
          </div>
        </v-card-actions>
      </v-card>
    </kinesis-element>
  </kinesis-container>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'AssetCard',
  mixins: [Utils],
  props: {
    asset: {
      required: true,
      type: Object
    }
  },
  computed: {
    thumbnailUrl() {
      return this.asset.thumbnailUrl || require('@/assets/img-not-found.png')
    }
  },
  methods: {
    imgError() {
      this.thumbnailUrl = require('@/assets/img-not-found.png')
    }
  }
}
</script>

<style scoped>
.actions {
  padding: 6px 12px 4px 0;
}
.asset-metadata {
  background-color: #333;
  background-color: rgba(51, 51, 51, 0.9);
  bottom: 0;
  color: #FFF;
  left: 0;
  position: absolute;
  right: 0;
}
</style>
