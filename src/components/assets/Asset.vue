<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary :anchor="`asset-${asset.id}`" :disabled="isLoading" />
    <div>
      <AssetPageHeader :asset="asset" :refresh-preview="refreshPreview" />
      <a id="skip-to-asset-overview" class="sr-only" href="#asset-overview">
        Skip to asset overview
      </a>
      <v-card class="mt-3 pa-2" outlined>
        <v-card-text>
          <AssetPreview :asset="asset" :contain="true" />
          <AssetOverview id="asset-overview" :asset="asset" />
        </v-card-text>
      </v-card>
      <div class="mt-3 px-2">
        <AssetComments :asset-id="asset.id" :update-comment-count="updateCommentCount" />
      </div>
    </div>
  </div>
</template>

<script>
import AssetComments from '@/components/assets/comments/AssetComments'
import AssetOverview from '@/components/assets/AssetOverview'
import AssetPageHeader from '@/components/assets/AssetPageHeader'
import AssetPreview from '@/components/assets/AssetPreview'
import AssetsSearch from '@/mixins/AssetsSearch'
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getAsset, refreshAssetPreview} from '@/api/assets'

export default {
  name: 'Asset',
  components: {
    AssetComments,
    AssetOverview,
    AssetPageHeader,
    AssetPreview,
    BackToAssetLibrary
  },
  mixins: [AssetsSearch, Context, Utils],
  data: () => ({
    asset: undefined,
    refreshPreviewTimeout: undefined
  }),
  created() {
    this.$loading()
    this.fetchAsset().then(() => {
      this.$ready(this.asset.title)
      this.rewriteBookmarkHash({assetId: this.asset.id})
    })
  },
  destroyed() {
    clearTimeout(this.refreshPreviewTimeout)
    this.clearBookmarkHash()
  },
  methods: {
    fetchAsset() {
      const assetId = this.$route.params.id
      if (assetId) {
        return getAsset(assetId).then(data => {
          this.asset = data
          this.updateAssetStore(this.asset)
          if (data && data.previewStatus === 'pending') {
            this.scheduleRefreshPreview()
          }
          this.$nextTick(this.resizeIFrame)
        })
      }
    },
    refreshPreview() {
      refreshAssetPreview(this.asset.id).then(() => {
        this.asset.previewStatus = 'pending'
        this.scheduleRefreshPreview()
      })
    },
    scheduleRefreshPreview() {
      clearTimeout(this.refreshPreviewTimeout)
      this.refreshPreviewTimeout = setTimeout(this.fetchAsset, 2000)
    },
    updateCommentCount(count) {
      this.asset.commentCount = count
      this.updateAssetStore({id: this.asset.id, commentCount: this.asset.commentCount})
    }
  }
}
</script>
