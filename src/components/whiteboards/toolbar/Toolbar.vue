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
        <TextTool />
        <PencilBrushTool />
        <ShapeTool />
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
      <AssetTool />
      <ExportTool />
      <EditWhiteboardTool />
    </v-toolbar>
  </v-card>
</template>

<script>
import AssetTool from '@/components/whiteboards/toolbar/AssetTool'
import Context from '@/mixins/Context'
import EditWhiteboardTool from '@/components/whiteboards/toolbar/EditWhiteboardTool'
import ExportTool from '@/components/whiteboards/toolbar/ExportTool'
import PencilBrushTool from '@/components/whiteboards/toolbar/PencilBrushTool'
import TextTool from '@/components/whiteboards/toolbar/TextTool'
import ShapeTool from '@/components/whiteboards/toolbar/ShapeTool'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Toolbar',
  mixins: [Context, Whiteboarding],
  components: {
    AssetTool,
    ExportTool,
    EditWhiteboardTool,
    PencilBrushTool,
    ShapeTool,
    TextTool
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
