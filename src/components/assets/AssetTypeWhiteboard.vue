<template>
  <v-main class="h-100 whiteboard-container">
    <div id="whiteboard-viewport" class="h-100">
      <canvas id="canvas" />
    </div>
  </v-main>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'AssetTypeWhiteboard',
  mixins: [Whiteboarding],
  props: {
    asset: {
      required: true,
      type: Object
    },
    maxHeight: {
      default: 720,
      required: false,
      type: Number
    }
  },
  created() {
    this.init(this.asset).then(asset => {
      this.setDisableAll(false)
      this.$ready(asset.title)
    })
  }
}
</script>

<style scoped>
.whiteboard-container {
  background-color: #fdfbf7;
}
</style>
