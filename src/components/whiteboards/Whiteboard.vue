<template>
  <v-app>
    <Toolbar />
    <Spinner v-if="isLoading" class="spinner" />
    <v-main id="whiteboard-container" class="h-100 whiteboard-container">
      <!-- 'tabindex' is necessary in order to attach DOM element listener. -->
      <div id="whiteboard-viewport" class="h-100 whiteboard-viewport" tabindex="0">
        <canvas id="canvas"></canvas>
      </div>
    </v-main>
  </v-app>
</template>

<script>
import Context from '@/mixins/Context'
import Spinner from '@/components/util/Spinner'
import Toolbar from '@/components/whiteboards/toolbar/Toolbar'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'
import {getWhiteboard} from '@/api/whiteboards'

export default {
  name: 'Whiteboard',
  mixins: [Context, Utils, Whiteboarding],
  components: {Spinner, Toolbar},
  data: () => ({
    isSnackbarOpen: false
  }),
  created() {
    this.$loading(true)
    const whiteboardId = parseInt(this.$route.params.id, 10)
    getWhiteboard(whiteboardId).then(whiteboard => {
      this.init({whiteboard, disable: true}).then(() => {
        this.$ready(this.whiteboard.title)
      })
    })
  }
}
</script>

<style scoped>
.spinner {
  z-index: 1200;
}
.whiteboard-container {
  background-color: #fdfbf7;
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
  z-index: 1000;
}
.whiteboard-viewport {
  overflow: scroll;
  position: relative;
}
</style>
