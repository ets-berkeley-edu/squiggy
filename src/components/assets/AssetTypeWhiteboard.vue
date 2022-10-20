<template>
  <v-main class="h-100 overflow-hidden position-relative whiteboard-container">
    <div id="whiteboard-viewport" class="h-100">
      <div class="zoom-tool-container">
        <Zoom />
      </div>
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
}
#whiteboard-viewport, .zoom-tool-container {
  width: 100%;
  height: 100%;
  position: absolute;
  top: 0;
  left: 0;
}
.zoom-tool-container {
  z-index: 10;
}
</style>
