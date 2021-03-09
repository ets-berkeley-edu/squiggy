<template>
  <div v-if="!loading">
    <BackToAssetLibrary :anchor="`asset-${asset.id}`" />
    <div>
      {{ asset }}
    </div>
  </div>
</template>

<script>
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import {getAsset} from '@/api/assets'

export default {
  name: 'Asset',
  components: {BackToAssetLibrary},
  mixins: [Context],
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
