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
    <v-card>
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Export whiteboard to Asset Library</h2>
      </v-card-title>
      <v-card-text>
        <v-container class="pb-0 pt-7 text-body-1">
          <v-row class="pb-2" no-gutters>
            <v-col class="pt-2" cols="3">
              <label>Foo</label>
            </v-col>
            <v-col cols="9">
              TODO
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ExportToolDialog',
  mixins: [Whiteboarding],
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
  }
}
</script>
