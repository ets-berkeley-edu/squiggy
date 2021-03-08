<template>
  <v-card>
    <v-sheet elevation="1">
      <v-img src="@/assets/mock-asset-preview.png">
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
    <v-card-actions>
      <div class="align-center d-flex justify-end w-100">
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
}
.asset-metadata small {
  font-size: 13px;
}
</style>
