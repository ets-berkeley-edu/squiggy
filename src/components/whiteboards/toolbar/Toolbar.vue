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
      <ZoomTool />
      <AssetTool />
      <ExportTool />
      <DeleteWhiteboardDialog
        :on-cancel="cancelDelete"
        :on-confirm-delete="deleteConfirmed"
        :open="isDeleteDialogOpen"
      />
      <SettingsTool :open-delete-dialog="openDeleteDialog" />
    </v-toolbar>
  </v-card>
</template>

<script>
import AssetTool from '@/components/whiteboards/toolbar/AssetTool'
import Context from '@/mixins/Context'
import DeleteWhiteboardDialog from '@/components/whiteboards/DeleteWhiteboardDialog'
import ExportTool from '@/components/whiteboards/toolbar/ExportTool'
import PencilBrushTool from '@/components/whiteboards/toolbar/PencilBrushTool'
import SettingsTool from '@/components/whiteboards/toolbar/SettingsTool'
import ShapeTool from '@/components/whiteboards/toolbar/ShapeTool'
import TextTool from '@/components/whiteboards/toolbar/TextTool'
import ZoomTool from '@/components/whiteboards/toolbar/ZoomTool'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Toolbar',
  mixins: [Context, Whiteboarding],
  components: {
    AssetTool,
    DeleteWhiteboardDialog,
    ExportTool,
    PencilBrushTool,
    SettingsTool,
    ShapeTool,
    TextTool,
    ZoomTool
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
    isDeleteDialogOpen: false
  }),
  methods: {
    cancelDelete() {
      this.$announcer.polite('Canceled')
      this.openDeleteDialog = false
    },
    deleteConfirmed() {
      this.openDeleteDialog = false
      this.deleteWhiteboard()
    },
    openDeleteDialog() {
      this.isDeleteDialogOpen = true
    }
  }
}
</script>
