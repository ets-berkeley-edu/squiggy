<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-export"
        class="mx-2"
        color="pink"
        dark
        fab
        input-value="menu"
        small
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">Export</span>
        <font-awesome-icon color="white" icon="download" />
      </v-btn>
    </template>
    <v-card v-if="exportability" class="pt-1">
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Export whiteboard to Asset Library</h2>
      </v-card-title>
      <v-list v-if="$canvas.getObjects().length">
        <v-list-item>
          <v-list-item-action class="mr-0 my-0 w-100">
            <ExportAsAsset :watch-dialog="watchChildDialog" />
          </v-list-item-action>
        </v-list-item>
        <v-list-item v-if="whiteboard && !exportability.errored.length && !exportability.pending.length">
          <v-list-item-action class="mr-0 my-0 w-100">
            <v-btn
              id="toolbar-download-as-image-btn"
              class="justify-start w-100"
              color="white"
              elevation="0"
              :href="`${$config.apiBaseUrl}/api/whiteboard/${whiteboard.id}/download/png`"
              @click="() => menu = false"
            >
              <font-awesome-icon icon="download" size="lg" />
              <span class="pl-3">Download as image</span>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
        <v-list-item v-if="exportability.errored.length" class="d-flex">
          <font-awesome-icon icon="exclamation-triangle" class="pr-2" />
          <div class="red--text">
            Whiteboard cannot be exported due to an asset processing error. Remove problematic assets and retry.
          </div>
        </v-list-item>
        <v-list-item v-if="exportability.pending.length">
          <font-awesome-icon icon="exclamation-triangle" class="pr-2" />
          <div class="red--text">Whiteboard cannot be exported yet, assets are still processing. Try again soon.</div>
        </v-list-item>
      </v-list>
      <v-card-text v-if="!$canvas.getObjects().length">
        <div class="pt-5 px-3 subtitle-1">
          When this whiteboard has one or more elements, it can be:
          <ul>
            <li>Downloaded as PNG file</li>
            <li>Exported to the Asset Library</li>
          </ul>
          Enjoy!
        </div>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'
import ExportAsAsset from '@/components/whiteboards/toolbar/assets/ExportAsAsset'
import {getExportabilitySummary} from '@/api/whiteboards'

export default {
  name: 'ExportTool',
  mixins: [Whiteboarding],
  components: {ExportAsAsset},
  data: () => ({
    exportability: undefined,
    menu: false
  }),
  watch: {
    menu(value) {
      if (value) {
        getExportabilitySummary(this.whiteboard.id).then(summary => {
          this.exportability = summary
        })
        this.$putFocusNextTick('menu-header')
      }
      this.setDisableAll(value)
    }
  },
  created() {
    getExportabilitySummary(this.whiteboard.id).then(summary => {
      this.exportability = summary
    })
  },
  methods: {
    watchChildDialog(isOpen) {
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
