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
        @keypress.enter="go(`/asset/${asset.id}`)"
        @click="go(`/asset/${asset.id}`)"
      >
        <v-sheet elevation="1">
          <v-img class="thumbnail" :src="thumbnailUrl" @error="setImageError">
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
                  <font-awesome-icon icon="thumbs-up" :class="{'asset-icon-liked': asset.liked}" />
                  {{ asset.likes }}
                  <span class="sr-only">{{ asset.likes === 1 ? 'like' : 'likes' }}</span>
                </div>
                <div class="pr-3">
                  <font-awesome-icon icon="eye" />
                  {{ asset.views }}
                  <span class="sr-only">{{ asset.views === 1 ? 'view' : 'views' }}</span>
                </div>
                <div>
                  <font-awesome-icon icon="comment" />
                  {{ asset.commentCount }}
                  <span class="sr-only">{{ asset.commentCount === 1 ? 'comment' : 'comments' }}</span>
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
  data: function() {
    return {
      imageError: false,
    }
  },
  computed: {
    thumbnailUrl: function () {
      if (!this.asset.thumbnailUrl || this.imageError) {
        return require('@/assets/img-not-found.png')
      }
      return this.asset.thumbnailUrl
    }
  },
  methods: {
    setImageError() {
      this.imageError = true
    }
  }
}
</script>

<style scoped>
.actions {
  padding: 6px 12px 4px 0;
}
.asset-icon-liked {
  color: #4172b4 !important;
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
