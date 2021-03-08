<template>
  <div>
    {{ asset }}
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import {getAsset} from '@/api/assets'

export default {
  name: 'Asset',
  mixins: [Context],
  data: () => ({
    asset: undefined
  }),
  created() {
    getAsset(this.$route.params.id).then(data => {
      this.asset = data
    })
    this.$ready('TODO: Asset name here')
  }
}
</script>
