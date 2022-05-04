<template>
  <v-app-bar
    v-if="whiteboard"
    app
    class="whiteboard-app-bar pl-0"
    :collapse="collapse"
    :collapse-on-scroll="!collapse"
    color="white"
    scroll-target="whiteboard-container"
  >
    <v-container class="px-0" fluid>
      <v-row justify="space-between" no-gutters>
        <v-col
          class="align-center d-flex justify-start"
          cols="4"
        >
          <div class="pr-2">
            <v-btn
              id="collapse-and-expand-the-app-bar"
              color="green"
              fab
              input-value="collapse"
              :small="!collapse"
              :x-small="collapse"
              @click="() => collapse = !collapse"
            >
              <font-awesome-icon
                color="white"
                :icon="collapse ? 'chevron-right' : 'chevron-left'"
                size="lg"
              />
            </v-btn>
          </div>
          <h1
            v-if="!collapse"
            id="whiteboard-title"
            class="whiteboard-title"
          >
            {{ whiteboard.title }}
          </h1>
        </v-col>
        <v-col v-if="!collapse" class="text-center" cols="4">
          <v-btn-toggle
            v-if="!whiteboard.isReadOnly"
            v-model="modeProxy"
            active-class="primary"
            background-color="white"
            borderless
          >
            <MoveTool />
            <ZoomTool />
            <TextTool />
            <PencilBrushTool />
            <ShapeTool />
            <AssetTool />
          </v-btn-toggle>
        </v-col>
        <v-col cols="4">
          <div class="align-center d-flex justify-end">
            <Users :collapse="collapse" />
            <ExportTool v-if="!collapse" />
            <SettingsTool
              v-if="!collapse && !whiteboard.isReadOnly || ($currentUser.isAdmin || $currentUser.isTeaching)"
              :open-delete-dialog="openDeleteDialog"
            />
          </div>
        </v-col>
      </v-row>
    </v-container>
    <DeleteWhiteboardDialog
      :on-cancel="cancelDelete"
      :on-confirm-delete="deleteConfirmed"
      :open="isDeleteDialogOpen"
    />
  </v-app-bar>
</template>

<script>
import AssetTool from '@/components/whiteboards/toolbar/AssetTool'
import Context from '@/mixins/Context'
import DeleteWhiteboardDialog from '@/components/whiteboards/DeleteWhiteboardDialog'
import ExportTool from '@/components/whiteboards/toolbar/ExportTool'
import MoveTool from '@/components/whiteboards/toolbar/MoveTool'
import PencilBrushTool from '@/components/whiteboards/toolbar/PencilBrushTool'
import SettingsTool from '@/components/whiteboards/toolbar/SettingsTool'
import ShapeTool from '@/components/whiteboards/toolbar/ShapeTool'
import TextTool from '@/components/whiteboards/toolbar/TextTool'
import Users from '@/components/whiteboards/sidebar/Users'
import Whiteboarding from '@/mixins/Whiteboarding'
import ZoomTool from '@/components/whiteboards/toolbar/ZoomTool'

export default {
  name: 'Toolbar2',
  mixins: [Context, Whiteboarding],
  components: {
    AssetTool,
    DeleteWhiteboardDialog,
    ExportTool,
    MoveTool,
    PencilBrushTool,
    SettingsTool,
    ShapeTool,
    TextTool,
    Users,
    ZoomTool
  },
  computed: {
    modeProxy: {
      get() {
        return this.mode
      },
      set(value) {
        this.setMode(value)
      }
    }
  },
  data: () => ({
    collapse: false,
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

<style scoped>
.whiteboard-app-bar {
  z-index: 1100;
}
.whiteboard-title {
  color: green;
  font-size: 20px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
