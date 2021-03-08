<template>
  <div>
    <v-btn
      id="asset-library-btn"
      class="bg-transparent"
      elevation="0"
      @click="go('/assets')"
    >
      <font-awesome-icon class="mr-2" icon="less-than" size="sm" />
      Back to Asset Library
    </v-btn>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'BackToAssetLibrary',
  mixins: [Utils]
}
</script>
