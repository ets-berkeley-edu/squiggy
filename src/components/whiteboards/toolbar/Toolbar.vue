<template>
  <v-app-bar
    v-if="whiteboard"
    app
    class="whiteboard-app-bar"
    :collapse="collapse"
    :collapse-on-scroll="!collapse"
    color="white"
    scroll-target="whiteboard-container"
  >
    <v-btn color="black" icon @click="() => collapse = !collapse">
      <span class="sr-only">{{ collapse }}</span>
      <font-awesome-icon :icon="collapse ? 'chevron-right' : 'chevron-left'" />
    </v-btn>
    <h1 v-show="!collapse" class="mood-ring whiteboard-title">
      {{ whiteboard.title }}
    </h1>

    <v-spacer></v-spacer>

    <v-btn-toggle
      v-if="!whiteboard.isReadOnly"
      v-model="modeProxy"
      active-class="primary"
      background-color="white"
      borderless
      :class="{'sr-only': collapse}"
    >
      <MoveTool />
      <ZoomTool />
      <TextTool />
      <PencilBrushTool />
      <ShapeTool />
      <AssetTool />
    </v-btn-toggle>

    <v-spacer></v-spacer>

    <Users :collapse="collapse" />
    <ExportTool v-if="!collapse" />
    <SettingsTool
      v-if="!collapse && !whiteboard.isReadOnly || ($currentUser.isAdmin || $currentUser.isTeaching)"
      :open-delete-dialog="openDeleteDialog"
    />
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
  font-size: 24px;
  max-width: 25%;
  overflow: hidden;
  padding-right: 15px;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.mood-ring {
  -webkit-animation:colorchange 300s infinite alternate;
}
@-webkit-keyframes colorchange {
  0% {
    color: darkgrey;
  }
  10% {
    color: #378dc5;
  }
  20% {
    color: #1abc9c;
  }
  30% {
    color: #d35400;
  }
  40% {
    color: #378dc5;
  }
  50% {
    color: white;
  }
  60% {
    color: #378dc5;
  }
  70% {
    color: #2980b9;
  }
  80% {
    color: #f1c40f;
  }
  90% {
    color: #2980b9;
  }
  100% {
    color: pink;
  }
}
</style>
