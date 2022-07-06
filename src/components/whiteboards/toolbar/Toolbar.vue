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
          <v-btn-toggle
            v-if="!whiteboard.isReadOnly"
            v-model="modeProxy"
            active-class="primary"
            background-color="white"
            class="ml-3"
            mandatory
          >
            <MoveTool />
            <ZoomTool />
            <TextTool />
            <PencilBrushTool />
            <ShapeTool />
            <AddExistingAssets />
            <AddLinkAsset />
            <UploadNewAsset />
          </v-btn-toggle>
        </v-col>
        <v-col cols="4">
          <div class="align-center d-flex justify-end">
            <Users />
            <ExportTool />
            <SettingsTool
              v-if="!whiteboard.isReadOnly || $currentUser.isAdmin || $currentUser.isTeaching"
              :open-delete-dialog="openDeleteDialog"
            />
          </div>
        </v-col>
      </v-row>
    </v-container>
    <DeleteWhiteboardDialog
      :is-deleting="isDeleting"
      :on-cancel="cancelDelete"
      :on-confirm-delete="deleteConfirmed"
      :open="isDeleteDialogOpen"
    />
  </v-app-bar>
</template>

<script>
import AddExistingAssets from '@/components/whiteboards/toolbar/assets/AddExistingAssets'
import AddLinkAsset from '@/components/whiteboards/toolbar/assets/AddLinkAsset'
import Context from '@/mixins/Context'
import DeleteWhiteboardDialog from '@/components/whiteboards/DeleteWhiteboardDialog'
import ExportTool from '@/components/whiteboards/toolbar/ExportTool'
import MoveTool from '@/components/whiteboards/toolbar/MoveTool'
import PencilBrushTool from '@/components/whiteboards/toolbar/PencilBrushTool'
import SettingsTool from '@/components/whiteboards/toolbar/SettingsTool'
import ShapeTool from '@/components/whiteboards/toolbar/ShapeTool'
import TextTool from '@/components/whiteboards/toolbar/TextTool'
import UploadNewAsset from '@/components/whiteboards/toolbar/assets/UploadNewAsset'
import Users from '@/components/whiteboards/toolbar/Users'
import Whiteboarding from '@/mixins/Whiteboarding'
import ZoomTool from '@/components/whiteboards/toolbar/ZoomTool'

export default {
  name: 'Toolbar',
  mixins: [Context, Whiteboarding],
  components: {
    AddExistingAssets,
    AddLinkAsset,
    DeleteWhiteboardDialog,
    ExportTool,
    MoveTool,
    PencilBrushTool,
    SettingsTool,
    ShapeTool,
    TextTool,
    UploadNewAsset,
    Users,
    ZoomTool
  },
  computed: {
    modeProxy: {
      get() {
        return this.mode
      },
      set(value) {
        if (value instanceof String) {
          this.setMode(value)
        }
      }
    }
  },
  data: () => ({
    isDeleteDialogOpen: false,
    isDeleting: false
  }),
  methods: {
    cancelDelete() {
      this.$announcer.polite('Canceled')
      this.isDeleteDialogOpen = false
    },
    deleteConfirmed() {
      this.isDeleting = true
      this.deleteWhiteboard().then(() => {
        this.isDeleteDialogOpen = false
        this.isDeleting = false
      })
    },
    openDeleteDialog() {
      this.isDeleteDialogOpen = true
    }
  }
}
</script>

<style scoped>
.whiteboard-app-bar {
  z-index: 1100;
}
</style>
