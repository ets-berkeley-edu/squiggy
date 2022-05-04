<template>
  <v-app>
    <Toolbar />
    <EditActiveFabricObject v-if="!isLoading && !whiteboard.isReadOnly" />
    <v-main id="whiteboard-container" class="whiteboard-container">
      <!-- 'tabindex' is necessary in order to attach DOM element listener. -->
      <div id="whiteboard-viewport" class="whiteboard-viewport" tabindex="0">
        <canvas id="canvas"></canvas>
      </div>
    </v-main>
    <div v-if="whiteboard">
      <Snackbar
        :timeout="3000"
        :top="true"
      >
        <h2 class="green--text text--lighten-2">Welcome!</h2>
        <div class="py-2 subtitle-2">
          <h3 class="green--text text--lighten-3">Whiteboard:</h3>
          {{ whiteboard.title }}
        </div>
        <div class="pb-2 subtitle-2">
          <h3 class="green--text text--lighten-3">Collaborator{{ whiteboard.users.length === 1 ? '' : 's' }}</h3>
          {{ oxfordJoin($_.map(whiteboard.users, 'canvasFullName')) }}
        </div>
      </Snackbar>
    </div>
  </v-app>
</template>

<script>
import Context from '@/mixins/Context'
import EditActiveFabricObject from '@/components/whiteboards/EditActiveFabricObject'
import Snackbar from '@/components/util/Snackbar'
import Toolbar from '@/components/whiteboards/toolbar/Toolbar'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'
import {getWhiteboard} from '@/api/whiteboards'

export default {
  name: 'Whiteboard',
  mixins: [Context, Utils, Whiteboarding],
  components: {Snackbar, EditActiveFabricObject, Toolbar},
  data: () => ({
    isSnackbarOpen: false,
    pingJob: undefined
  }),
  created() {
    this.$loading()
    const whiteboardId = parseInt(this.$route.params.id, 10)
    getWhiteboard(whiteboardId).then(whiteboard => {
      this.init(whiteboard).then(whiteboard => {
        this.setDisableAll(false)
        this.$ready(whiteboard.title)
        if (!this.whiteboard.isReadOnly) {
          clearTimeout(this.pingJob)
          this.pingJob = setTimeout(this.keepSocketAlive, 60000)
        }
      })
    })
  },
  destroyed() {
    clearTimeout(this.pingJob)
  },
  methods: {
    keepSocketAlive() {
      this.ping()
      this.pingJob = setTimeout(this.keepSocketAlive, 60000)
    }
  }
}
</script>

<style scoped>
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
  height: 100vh;
  overflow: scroll;
  position: relative;
}
</style>
