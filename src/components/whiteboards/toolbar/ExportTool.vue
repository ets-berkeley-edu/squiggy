<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    max-width="500"
    width="500"
  >
    <template #activator="activator">
      <v-tooltip bottom>
        <template #activator="tooltip">
          <v-btn
            id="toolbar-export"
            class="mx-2"
            color="green"
            dark
            fab
            input-value="menu"
            small
            v-bind="activator.attrs"
            v-on="{...activator.on, ...tooltip.on}"
          >
            <font-awesome-icon color="white" icon="download" size="lg" />
          </v-btn>
        </template>
        <span>{{ tooltipText }}</span>
      </v-tooltip>
    </template>
    <v-card class="pt-1">
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Export whiteboard to Asset Library</h2>
      </v-card-title>
      <v-list v-if="$canvas.getObjects().length">
        <v-list-item>
          <v-list-item-action class="mr-0 my-0 w-100">
            <ExportAsAsset :watch-dialog="watchChildDialog" />
          </v-list-item-action>
        </v-list-item>
        <v-list-item v-if="!$_.intersection(assetPreviewStatuses, ['error', 'pending']).length">
          <v-list-item-action class="mr-0 my-0 w-100">
            <v-btn
              id="toolbar-download-as-image-btn"
              class="justify-start w-100"
              color="white"
              elevation="0"
              :href="`${$config.apiBaseUrl}/api/whiteboard/${whiteboard.id}/download/png`"
              @click="() => menu = false"
            >
              <font-awesome-icon icon="image" size="lg" />
              <div class="pl-3">Download as image</div>
            </v-btn>
          </v-list-item-action>
        </v-list-item>
        <v-list-item v-if="assetPreviewStatuses.includes('error')" class="align-start d-flex">
          <div class="ml-4 mr-3 pt-1">
            <font-awesome-icon
              class="red--text"
              icon="exclamation-triangle"
              size="lg"
            />
          </div>
          <div class="red--text">
            Whiteboard cannot be exported due to an asset processing error.
            Remove problematic assets and retry.
          </div>
        </v-list-item>
        <v-list-item v-if="assetPreviewStatuses.includes('pending')" class="align-start d-flex pb-2">
          <div class="ml-4 mr-3 pt-1">
            <font-awesome-icon
              class="red--text"
              icon="exclamation-triangle"
              size="lg"
            />
          </div>
          <div class="red--text">
            Whiteboard cannot be exported yet, assets are still processing.
            Try again soon.
          </div>
        </v-list-item>
      </v-list>
      <v-card-text v-if="!$canvas.getObjects().length">
        <div class="pt-5 px-3 text-subtitle-1">
          When this whiteboard has one or more elements, it can be:
          <ul class="py-2">
            <li>Downloaded as PNG file</li>
            <li>Exported to the Asset Library</li>
          </ul>
          <div class="py-2">
            Enjoy!
          </div>
        </div>
      </v-card-text>
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
    menu: false,
    tooltipText: 'Export this whiteboard'
  }),
  computed: {
    assetPreviewStatuses() {
      const key = 'assetPreviewStatus'
      return this.whiteboard ? this.$_.map(this.$_.filter(this.whiteboard.whiteboardElements, key), key) : []
    }
  },
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
