<template>
  <div>
    <div>
      <AddAssetsDialog
        :hide-managed-assets-button="true"
        :on-cancel="$_.noop"
        :on-save="$_.noop"
      />
    </div>
    <div class="pa-10">
      {{ whiteboard }}
    </div>
  </div>
</template>

<script>
import AddAssetsDialog from '@/components/whiteboards/AddAssetsDialog'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {getWhiteboard} from '@/api/whiteboards'

export default {
  name: 'Whiteboard',
  components: {AddAssetsDialog},
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
  },
  methods: {
    addAsset() {

    }
  }
}
</script>

<style scoped>

</style>