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
          :whiteboard="whiteboard"
          :on-cancel="cancel"
          :on-ready="() => $announcer.polite('The edit Whiteboard dialog is ready.')"
          :after-save="afterSave"
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
    cancel() {
      this.$announcer.polite('Canceled')
      this.menu = false
    },
    afterSave(whiteboard) {
      this.onWhiteboardUpdate(whiteboard)
      this.menu = false
    }
  }
}
</script>
