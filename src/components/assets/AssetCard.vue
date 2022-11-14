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
        :aria-pressed="ariaPressed"
        class="card-class"
        hover
        tabindex="-1"
        @keypress.enter="onClick"
        @click="onClick"
      >
        <v-sheet elevation="1">
          <v-img
            aspect-ratio="1"
            class="thumbnail"
            :src="thumbnailUrl"
            @error="setImageError"
          >
            <v-card-text :class="`${context}-asset-metadata`">
              <slot>
                <a
                  href="#"
                  class="d-flex flex-column text-decoration-none white--text"
                  @click="onClick"
                  @keydown.enter="onClick"
                >
                  <span class="font-weight-bold mb-1">
                    {{ asset.title }}
                  </span>
                  <span>
                    by {{ oxfordJoin($_.map(asset.users, 'canvasFullName')) }}
                  </span>
                </a>
              </slot>
            </v-card-text>
          </v-img>
        </v-sheet>
      </v-card>
      <div
        v-if="!hideEngagementCounts"
        class="actions align-center d-flex justify-end w-100"
      >
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
    </kinesis-element>
  </kinesis-container>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'AssetCard',
  mixins: [Utils],
  props: {
    ariaPressed: {
      required: false,
      type: Boolean
    },
    asset: {
      required: true,
      type: Object
    },
    context: {
      default: 'asset-library',
      required: false,
      type: String
    },
    hideEngagementCounts: {
      required: false,
      type: Boolean
    },
    onAssetClick: {
      default: undefined,
      required: false,
      type: Function
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
    onClick() {
      if (this.onAssetClick) {
        this.onAssetClick(this.asset)
      } else {
        this.go(`/asset/${this.asset.id}`)
      }
    },
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
.asset-library-asset-metadata {
  background-color: rgba(51, 51, 51, 0.9);
  bottom: 0;
  color: #FFF;
  left: 0;
  position: absolute;
  right: 0;
}
.whiteboard-asset-metadata {
  background-color: rgba(51, 51, 51, 0.9);
  bottom: 0;
  color: #FFF;
  left: 0;
  margin-top: 0;
  padding-bottom: 0;
  padding-top: 0;
  position: absolute;
  right: 0;
}
.card-class {
  height: 100%;
}
.card-class:active, .card-class:focus {
  background-color: #378dc5;
}
.card-class:hover {
  background-color: #67bdf5;
}
</style>
