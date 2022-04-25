<template>
  <v-dialog
    v-model="menu"
    width="800"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-settings"
        color="white"
        dense
        :disabled="disableAll"
        elevation="1"
        height="48px"
        rounded
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">Settings</span>
        <font-awesome-icon color="grey" icon="cog" size="2x" />
      </v-btn>
    </template>
    <v-card>
      <v-card-text>
        <EditWhiteboard
          class="pt-10"
          :after-save="afterSave"
          :on-click-delete="onClickDelete"
          :on-cancel="cancel"
          :on-ready="() => $announcer.polite('The edit Whiteboard dialog is ready.')"
          :reset="menu"
          :whiteboard="whiteboard"
        />
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
import EditWhiteboard from '@/components/whiteboards/EditWhiteboard'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'EditWhiteboardTool',
  mixins: [Whiteboarding],
  components: {EditWhiteboard},
  props: {
    openDeleteDialog: {
      required: true,
      type: Function
    }
  },
  data: () => ({
    menu: false
  }),
  watch: {
    menu(value) {
      if (value) {
        this.setMode('move')
        this.$putFocusNextTick('menu-header')
      }
      this.setDisableAll(value)
    }
  },
  beforeDestroy() {
    this.setDisableAll(false)
  },
  methods: {
    afterSave(whiteboard) {
      this.onWhiteboardUpdate(whiteboard)
      this.menu = false
    },
    cancel() {
      this.$announcer.polite('Canceled')
      this.menu = false
    },
    onClickDelete() {
      this.menu = false
      this.openDeleteDialog()
    }
  }
}
</script>
