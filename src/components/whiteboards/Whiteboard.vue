<template>
  <v-app>
    <OnlineUsers />
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
import OnlineUsers from '@/components/whiteboards/OnlineUsers'
import Toolbar from '@/components/whiteboards/toolbar/Toolbar'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Whiteboard',
  mixins: [Context, Utils, Whiteboarding],
  components: {OnlineUsers, Toolbar},
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
  background-color: aqua;
  bottom: 0;
  left: 0;
  position: absolute;
  right: 0;
  top: 0;
}
.whiteboard-viewport {
  height: 100vh;
  overflow: scroll;
  position: relative;
}
</style>
