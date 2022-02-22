<template>
  <div>
    {{ whiteboard }}
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getWhiteboard} from '@/api/whiteboards'

export default {
  name: 'Whiteboard',
  components: {
  },
  mixins: [Context, Utils],
  data: () => ({
    whiteboard: undefined
  }),
  created() {
    this.$loading()
    const whiteboardId = this.$route.params.id
    // TODO: Wire up real socket IO per https://flask-socketio.readthedocs.io/
    const mockSocketId = new Date().getTime()
    getWhiteboard(whiteboardId, mockSocketId).then(data => {
      this.whiteboard = data
      this.$ready()
    })
  }
}
</script>

<style scoped>

</style>