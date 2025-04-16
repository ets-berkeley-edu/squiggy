<template>
  <v-app-bar
    v-if="whiteboard"
    app
    class="whiteboard-app-bar pl-0"
    color="white"
  >
    <v-container class="px-0" fluid>
      <v-row justify="space-between" no-gutters>
        <v-col class="align-center d-flex" cols="8">
          <h1 id="whiteboard-title" class="sr-only">{{ whiteboard.title }}</h1>
          <Zoom
            color="teal lighten-3"
            :dark-theme-buttons="true"
          />
          <div v-if="whiteboard.deletedAt" class="pl-2">
            This whiteboard was deleted on {{ whiteboard.deletedAt | moment('dddd, MMMM Do YYYY') }}.
          </div>
        </v-col>
        <v-col cols="4">
          <div class="align-center d-flex justify-end">
            <ExportTool />
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-app-bar>
</template>

<script>
import Context from '@/mixins/Context'
import ExportTool from '@/components/whiteboards/toolbar/ExportTool'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'
import Zoom from '@/components/whiteboards/toolbar/Zoom'

export default {
  name: 'Toolbar',
  mixins: [Context, Utils, Whiteboarding],
  components: {
    ExportTool,
    Zoom
  }
}
</script>

<style scoped>
.whiteboard-app-bar {
  z-index: 1100;
}
</style>
