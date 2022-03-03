<template>
  <v-toolbar id="whiteboard-toolbar" dense>
    <v-card class="mr-auto" outlined tile>
      <v-btn-toggle v-model="selected">
        <v-btn id="toolbar-pointer" value="pointer">
          <span class="sr-only">Move and transform</span>
          <font-awesome-icon icon="mouse-pointer" />
        </v-btn>
        <v-btn id="toolbar-font" value="text">
          <span class="sr-only">Text</span>
          <font-awesome-icon icon="font" />
        </v-btn>
        <v-btn id="toolbar-paint" value="draw">
          <span class="sr-only">Draw</span>
          <font-awesome-icon icon="paint-brush" />
        </v-btn>
        <v-btn id="toolbar-shape" value="shape">
          <span class="sr-only">Shape</span>
          <font-awesome-icon icon="shapes" />
        </v-btn>
      </v-btn-toggle>
    </v-card>
    <v-card outlined tile>
      <v-btn-toggle v-model="selected">
        <v-btn id="toolbar-fit-to-screen" value="fitToScreen">
          <span class="sr-only">Fit to screen</span>
          <font-awesome-icon icon="search-minus" />
        </v-btn>
        <v-btn id="toolbar-actual-size" value="actualSize">
          <span class="sr-only">Actual size"</span>
          <font-awesome-icon icon="search-plus" />
        </v-btn>
      </v-btn-toggle>
      <v-btn-toggle v-model="selected">
        <v-btn id="toolbar-add-asset" value="addAsset">
          <font-awesome-icon icon="circle-plus" />
          <span class="pl-2">Asset</span>
        </v-btn>
      </v-btn-toggle>
      <v-btn-toggle v-model="selected">
        <v-btn id="toolbar-undo" value="undo">
          <span class="sr-only">Undo</span>
          <font-awesome-icon icon="reply" />
        </v-btn>
        <v-btn id="toolbar-redo" value="redo">
          <span class="sr-only">Redo</span>
          <font-awesome-icon icon="share" />
        </v-btn>
      </v-btn-toggle>
      <v-btn-toggle v-model="selected">
        <v-btn id="toolbar-export" value="export">
          <span class="sr-only">Export</span>
          <font-awesome-icon icon="download" />
        </v-btn>
        <v-btn id="toolbar-settings" value="settings">
          <span class="sr-only">Settings</span>
          <font-awesome-icon icon="cog" />
        </v-btn>
      </v-btn-toggle>
    </v-card>
  </v-toolbar>
</template>

<script>
import Context from '@/mixins/Context'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'WhiteboardToolbar',
  mixins: [Context, Whiteboarding],
  data: () => ({
    selected: undefined
  }),
  watch: {
    selected(newValue, oldValue) {
      console.log(`selected: ${newValue} (was ${oldValue})`)
    }
  }
}
</script>
