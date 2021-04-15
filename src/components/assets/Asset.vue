<template>
  <div v-if="!isLoading">
    <BackToAssetLibrary :anchor="`asset-${asset.id}`" :disabled="isLoading" />
    <div>
      <AssetPageHeader :asset="asset" />
      <v-card class="mt-3 pa-2" outlined>
        <v-card-text>
          <div class="asset-image-container">
            <AssetPreview :asset="asset" :contain="true" />
          </div>
          <AssetOverview :asset="asset" />
        </v-card-text>
      </v-card>
      <!--
      TODO: Will Activity-Timeline suffer the fate of the Impact Studio? I.e., will it go away?
      <AssetActivityTimeline :asset="asset" />
      -->
      <div class="mt-3 px-2">
        <AssetComments :asset-id="asset.id" />
      </div>
    </div>
  </div>
</template>

<script>
import AssetComments from '@/components/assets/comments/AssetComments'
import AssetOverview from '@/components/assets/AssetOverview'
import AssetPageHeader from '@/components/assets/AssetPageHeader'
import AssetPreview from '@/components/assets/AssetPreview'
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getAsset} from '@/api/assets'

export default {
  name: 'Asset',
  components: {
    AssetComments,
    AssetOverview,
    AssetPageHeader,
    AssetPreview,
    BackToAssetLibrary
  },
  mixins: [Context, Utils],
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
      return getAsset(this.$route.params.id).then(data => {
        this.asset = data
        if (data && data.previewStatus === 'pending') {
          this.scheduleRefreshPreview()
        }
      })
    },
    scheduleRefreshPreview() {
      clearTimeout(this.refreshPreviewTimeout)
      this.refreshPreviewTimeout = setTimeout(this.fetchAsset, 2000)
    }
  }
}
</script>
