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
          :disabled="disableAll"
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
      <DeleteWhiteboardDialog
        :on-cancel="cancelDelete"
        :on-confirm-delete="deleteConfirmed"
        :open="isDeleteDialogOpen"
      />
      <EditWhiteboardTool :open-delete-dialog="openDeleteDialog" />
    </v-toolbar>
  </v-card>
</template>

<script>
import AssetTool from '@/components/whiteboards/toolbar/AssetTool'
import Context from '@/mixins/Context'
import DeleteWhiteboardDialog from '@/components/whiteboards/DeleteWhiteboardDialog'
import EditWhiteboardTool from '@/components/whiteboards/toolbar/EditWhiteboardTool'
import ExportTool from '@/components/whiteboards/toolbar/ExportTool'
import PencilBrushTool from '@/components/whiteboards/toolbar/PencilBrushTool'
import TextTool from '@/components/whiteboards/toolbar/TextTool'
import ShapeTool from '@/components/whiteboards/toolbar/ShapeTool'
import Whiteboarding from '@/mixins/Whiteboarding'
import {deleteWhiteboard} from '@/api/whiteboards'

export default {
  name: 'Toolbar',
  mixins: [Context, Whiteboarding],
  components: {
    AssetTool,
    DeleteWhiteboardDialog,
    EditWhiteboardTool,
    ExportTool,
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
    isDeleteDialogOpen: false,
    toggle: 2
  }),
  methods: {
    cancelDelete() {
      this.$announcer.polite('Canceled')
      this.openDeleteDialog = false
    },
    deleteConfirmed() {
      this.openDeleteDialog = false
      deleteWhiteboard(this.whiteboard.id).then(window.close)
    },
    openDeleteDialog() {
      this.isDeleteDialogOpen = true
    }
  }
}
</script>
