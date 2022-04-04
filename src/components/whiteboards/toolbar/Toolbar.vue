<template>
  <v-app-bar
    app
    bottom
    dense
    outlined
  >
    <v-btn id="toolbar-pointer" icon>
      <span class="sr-only">Move and transform</span>
      <font-awesome-icon icon="arrows-up-down-left-right" />
    </v-btn>
    <TextToolDialog />
    <DrawToolDialog />
    <ShapeToolDialog />
    <v-btn id="toolbar-fit-to-screen" icon>
      <span class="sr-only">Fit to screen</span>
      <font-awesome-icon icon="search-minus" />
    </v-btn>
    <v-btn id="toolbar-actual-size" icon>
      <span class="sr-only">Actual size"</span>
      <font-awesome-icon icon="search-plus" />
    </v-btn>
    <AssetToolDialog />
    <v-btn id="toolbar-export" icon>
      <span class="sr-only">Export</span>
      <font-awesome-icon icon="download" />
    </v-btn>
    <v-btn id="toolbar-settings" icon>
      <span class="sr-only">Settings</span>
      <font-awesome-icon icon="cog" />
    </v-btn>
    <v-btn icon @click="unlock">
      <font-awesome-icon icon="unlock" />
    </v-btn>
  </v-app-bar>
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
    collapsed: false
  }),
  methods: {
    unlock() {
      this.setDisableAll(false)
    }
  }
}
</script>
