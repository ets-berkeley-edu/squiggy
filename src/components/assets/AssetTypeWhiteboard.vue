<template>
  <v-main class="h-100 overflow-hidden py-0 whiteboard-container">
    <div class="align-center d-flex mb-3">
      <div class="pr-3">
        <Zoom btn-toggle-class="justify-start" />
      </div>
      <div class="pr-1 subtitle-1">
        <font-awesome-icon
          class="yellow--text"
          icon="exclamation-triangle"
          size="lg"
        />
      </div>
      <div class="subtitle-1">
        <span class="font-weight-bold">To re-position the image, hold down the Option (or Alt) key and then drag your mouse cursor.</span>
      </div>
    </div>
    <div
      id="whiteboard-viewport"
      class="canvas-container h-100"
      tabindex="0"
    >
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
  position: relative;
  z-index: 1000;
}
</style>
