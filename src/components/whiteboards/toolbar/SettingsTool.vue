<template>
  <v-dialog
    v-model="menu"
    max-width="800"
    scrollable
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-settings"
        class="mx-2"
        color="indigo"
        dark
        fab
        input-value="menu"
        small
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">Edit</span>
        <font-awesome-icon color="white" icon="cog" />
      </v-btn>
    </template>
    <v-card>
      <v-card-text class="scrollable-card">
        <RestoreWhiteboard
          v-if="whiteboard.deletedAt"
          :restore="restore"
          :on-cancel="close"
        />
        <EditWhiteboard
          v-if="!whiteboard.deletedAt"
          class="pt-10"
          :after-save="afterSave"
          :on-click-delete="onClickDelete"
          :on-cancel="close"
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
import RestoreWhiteboard from '@/components/whiteboards/toolbar/RestoreWhiteboard'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'SettingsTool',
  mixins: [Whiteboarding],
  components: {EditWhiteboard, RestoreWhiteboard},
  props: {
    openDeleteDialog: {
      default: () => {},
      required: false,
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
    afterSave(updated) {
      this.onWhiteboardUpdate(updated).then(this.close)
    },
    close() {
      this.menu = false
      this.$announcer.polite('Settings tool closed.')
    },
    onClickDelete() {
      this.close()
      this.openDeleteDialog()
    },
    restore() {
      this.menu = false
      this.setDisableAll(true)
      this.$loading()
      this.undeleteWhiteboard().then(() => {
        this.$announcer.polite('Whiteboard restored')
      })
    }
  }
}
</script>

<style scoped>
.scrollable-card {
  max-height: 75vh;
}
</style>
