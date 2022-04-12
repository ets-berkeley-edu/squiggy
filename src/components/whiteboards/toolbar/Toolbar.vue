<template>
  <v-card
    class="mx-auto transparent"
    elevation="0"
    style="margin-top: -64px;"
    max-width="700px"
  >
    <v-toolbar
      bottom
      color="transparent"
      dense
      elevation="0"
    >
      <v-btn-toggle
        v-model="modeProxy"
        active-class="primary"
        rounded
      >
        <v-btn
          id="toolbar-move-btn"
          class="pr-2"
          icon
          value="move"
          width="55px"
        >
          <span class="sr-only">Move and transform</span>
          <font-awesome-icon
            :color="mode === 'move' ? 'white' : 'grey'"
            icon="arrows-up-down-left-right"
            size="2x"
          />
        </v-btn>
        <TextToolDialog />
        <DrawToolDialog />
        <ShapeToolDialog />
      </v-btn-toggle>
      <v-btn
        id="toolbar-fit-to-screen"
        class="mx-2"
        color="white"
        dense
        elevation="1"
        height="48px"
        rounded
        @click="toggleZoom"
      >
        <span class="sr-only">{{ fitToScreen ? 'Actual size' : 'Fit to screen' }}</span>
        <font-awesome-icon color="grey" :icon="fitToScreen ? 'search-plus' : 'search-minus'" size="2x" />
      </v-btn>
      <AssetToolDialog />
      <ExportToolDialog />
      <EditWhiteboardDialog />
    </v-toolbar>
  </v-card>
</template>

<script>
import AssetToolDialog from '@/components/whiteboards/toolbar/AssetToolDialog'
import Context from '@/mixins/Context'
import DrawToolDialog from '@/components/whiteboards/toolbar/DrawToolDialog'
import EditWhiteboardDialog from '@/components/whiteboards/toolbar/EditWhiteboardDialog'
import ExportToolDialog from '@/components/whiteboards/toolbar/ExportToolDialog'
import TextToolDialog from '@/components/whiteboards/toolbar/TextToolDialog'
import ShapeToolDialog from '@/components/whiteboards/toolbar/ShapeToolDialog'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Toolbar',
  mixins: [Context, Whiteboarding],
  components: {
    AssetToolDialog,
    DrawToolDialog,
    ExportToolDialog,
    EditWhiteboardDialog,
    ShapeToolDialog,
    TextToolDialog
  },
  computed: {
    modeProxy: {
      get() {
        return this.mode
      },
      set(value) {
        console.log('setMode: ' + value)
        this.setMode(value)
      }
    }
  },
  data: () => ({
    toggle: 2
  })
}
</script>

<style scoped>
.toolbar {
  z-index: 1100;
}
</style>
