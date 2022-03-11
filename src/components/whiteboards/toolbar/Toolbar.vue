<template>
  <v-toolbar
    class="pt-1"
    floating
    prominent
  >
    <div class="pr-4">
      <v-btn @click="unlock">
        <font-awesome-icon icon="unlock" size="2x" />
      </v-btn>
      <v-btn id="toolbar-pointer" value="pointer">
        <span class="sr-only">Move and transform</span>
        <font-awesome-icon icon="arrows-up-down-left-right" size="2x" />
      </v-btn>
      <TextToolDialog />
      <DrawToolDialog />
      <ShapeToolDialog />
    </div>
    <div class="pr-4">
      <v-btn id="toolbar-fit-to-screen" value="fitToScreen">
        <span class="sr-only">Fit to screen</span>
        <font-awesome-icon icon="search-minus" size="2x" />
      </v-btn>
      <v-btn id="toolbar-actual-size" value="actualSize">
        <span class="sr-only">Actual size"</span>
        <font-awesome-icon icon="search-plus" size="2x" />
      </v-btn>
    </div>
    <div class="pr-4">
      <AssetToolDialog />
    </div>
    <v-btn id="toolbar-export" value="export">
      <span class="sr-only">Export</span>
      <font-awesome-icon icon="download" size="2x" />
    </v-btn>
    <v-btn id="toolbar-settings" value="settings">
      <span class="sr-only">Settings</span>
      <font-awesome-icon icon="cog" size="2x" />
    </v-btn>
  </v-toolbar>
</template>

<script>
import AssetToolDialog from '@/components/whiteboards/toolbar/AssetToolDialog'
import Context from '@/mixins/Context'
import DrawToolDialog from '@/components/whiteboards/toolbar/DrawToolDialog'
import TextToolDialog from '@/components/whiteboards/toolbar/TextToolDialog'
import ShapeToolDialog from '@/components/whiteboards/toolbar/ShapeToolDialog'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Toolbar',
  mixins: [Context, Whiteboarding],
  components: {
    AssetToolDialog,
    DrawToolDialog,
    ShapeToolDialog,
    TextToolDialog
  },
  data: () => ({
    selected: undefined
  }),
  methods: {
    unlock() {
      this.setDisableAll(false)
      this.selected = undefined
    }
  }
}
</script>
