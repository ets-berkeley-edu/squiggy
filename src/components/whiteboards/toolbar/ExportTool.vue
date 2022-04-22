<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    top
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-export"
        class="mx-2"
        color="white"
        dense
        :disabled="disableAll"
        elevation="1"
        height="48px"
        rounded
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">Export</span>
        <font-awesome-icon color="grey" icon="download" size="2x" />
      </v-btn>
    </template>
    <v-card class="pb-2">
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Export whiteboard to Asset Library</h2>
      </v-card-title>
      <v-list>
        <v-list-item>
          <v-list-item-action class="mr-0 w-100">
            <ExportAsAsset :watch-dialog="watchChildDialog" />
          </v-list-item-action>
        </v-list-item>
        <v-list-item v-if="whiteboard">
          <v-list-item-action class="mr-0 w-100">
            <v-btn
              id="toolbar-download-as-image-btn"
              class="d-flex justify-start w-100"
              :disabled="!whiteboard.whiteboardElements.length"
              :href="`${$config.apiBaseUrl}/api/whiteboard/${whiteboard.id}/export/png`"
              link
              text
              @click="() => menu = false"
            >
              Download as image
            </v-btn>
          </v-list-item-action>
        </v-list-item>
      </v-list>
    </v-card>
  </v-menu>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'
import ExportAsAsset from '@/components/whiteboards/toolbar/assets/ExportAsAsset'

export default {
  name: 'ExportTool',
  mixins: [Whiteboarding],
  components: {ExportAsAsset},
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
  methods: {
    watchChildDialog(isOpen) {
      this.setHideSidebar(isOpen)
      if (isOpen) {
        this.menu = false
      }
    }
  },
  beforeDestroy() {
    this.setDisableAll(false)
  }
}
</script>
