<template>
  <v-main class="h-100 overflow-hidden whiteboard-container">
    <Zoom />
    <div id="whiteboard-viewport" class="h-100" tabindex="0">
      <canvas id="canvas" />
    </div>
  </v-main>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'
import Zoom from '@/components/whiteboards/toolbar/Zoom'

export default {
  name: 'AssetTypeWhiteboard',
  mixins: [Whiteboarding],
  components: {Zoom},
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
    this.init({whiteboard: this.asset, disable: true}).then(() => {
      this.$ready(this.asset.title)
    })
  }
}
</script>

<style scoped>
.whiteboard-container {
  background-color: #fdfbf7;
  position: relative;
  z-index: 1000;
}
</style>
