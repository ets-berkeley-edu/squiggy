<template>
  <v-app>
    <Toolbar />
    <EditActiveFabricObject v-if="!isLoading && !whiteboard.isReadOnly" />
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
import EditActiveFabricObject from '@/components/whiteboards/EditActiveFabricObject'
import Spinner from '@/components/util/Spinner'
import Toolbar from '@/components/whiteboards/toolbar/Toolbar'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'
import {getWhiteboard} from '@/api/whiteboards'

export default {
  name: 'Whiteboard',
  mixins: [Context, Utils, Whiteboarding],
  components: {EditActiveFabricObject, Spinner, Toolbar},
  data: () => ({
    isSnackbarOpen: false,
    refreshJob: undefined
  }),
  created() {
    this.$loading(true)
    const whiteboardId = parseInt(this.$route.params.id, 10)
    getWhiteboard(whiteboardId).then(whiteboard => {
      this.init(whiteboard).then(whiteboard => {
        this.setDisableAll(false)
        this.$ready(whiteboard.title)
        if (!this.whiteboard.isReadOnly) {
          this.scheduleRefresh()
        }
      })
    })
  },
  destroyed() {
    clearTimeout(this.refreshJob)
  },
  methods: {
    scheduleRefresh() {
      clearTimeout(this.refreshJob)
      this.refreshJob = setTimeout(() => {
        this.checkForUpdates().then(() => {
          this.scheduleRefresh()
        })
      }, this.$config.whiteboardsRefreshInterval)
    }
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
  overflow: hidden;
  position: relative;
}
</style>
