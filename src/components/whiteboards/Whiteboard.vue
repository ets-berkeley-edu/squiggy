<template>
  <v-app>
    <div v-if="!isLoading">
      <OnlineUsers v-if="sessions" />
      <EditActiveFabricObject />
    </div>
    <Toolbar />
    <v-main id="whiteboard-container" class="whiteboard-container">
      <div id="whiteboard-viewport" class="whiteboard-viewport">
        <canvas id="canvas"></canvas>
      </div>
    </v-main>
  </v-app>
</template>

<script>
import Context from '@/mixins/Context'
import EditActiveFabricObject from '@/components/whiteboards/EditActiveFabricObject'
import OnlineUsers from '@/components/whiteboards/OnlineUsers'
import Toolbar from '@/components/whiteboards/toolbar/Toolbar'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Whiteboard',
  mixins: [Context, Utils, Whiteboarding],
  components: {EditActiveFabricObject, OnlineUsers, Toolbar},
  created() {
    this.$loading()
    this.init(this.$route.params.id).then(() => {
      this.setDisableAll(false)
      this.$ready()
    })
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
