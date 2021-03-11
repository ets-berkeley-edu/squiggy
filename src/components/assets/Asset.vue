<template>
  <div v-if="!loading">
    <BackToAssetLibrary :anchor="`asset-${asset.id}`" />

    <AssetPageHeader :asset="asset" />

    <AssetOverview :asset="asset" />

    <AssetActivityTimeline :asset="asset" />

    <AssetComments :asset="asset" />

    <pre>
      {{ asset }}
    </pre>
  </div>
</template>

<script>
import AssetActivityTimeline from '@/components/assets/AssetActivityTimeline'
import AssetComments from '@/components/assets/AssetComments'
import AssetOverview from '@/components/assets/AssetOverview'
import AssetPageHeader from '@/components/assets/AssetPageHeader'
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getAsset} from '@/api/assets'

export default {
  name: 'Asset',
  components: {AssetActivityTimeline, AssetComments, AssetOverview, AssetPageHeader, BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    asset: undefined
  }),
  created() {
    this.$loading()
    getAsset(this.$route.params.id).then(data => {
      this.asset = data
      this.$ready(this.asset.title)
    })
  }
}
</script>
