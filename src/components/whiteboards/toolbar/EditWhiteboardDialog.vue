<template>
  <v-dialog
    v-model="menu"
    :close-on-content-click="false"
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
          :whiteboard="whiteboard"
          :on-cancel="cancel"
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
  name: 'EditWhiteboardDialog',
  mixins: [Whiteboarding],
  components: {EditWhiteboard},
  data: () => ({
    menu: false
  }),
  watch: {
    menu(value) {
      if (value) {
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
      this.afterWhiteboardUpdate(whiteboard)
      this.menu = false
    }
  }
}
</script>
