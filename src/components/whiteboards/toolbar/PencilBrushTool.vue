<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-draw-btn"
        :disabled="disableAll"
        icon
        value="draw"
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">Draw</span>
        <font-awesome-icon :color="mode === 'draw' ? 'white' : 'grey'" icon="paintbrush" />
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Select brush and color</h2>
      </v-card-title>
      <v-card-text>
        <v-container class="pb-0 pt-7 text-body-1">
          <v-row class="pb-2" no-gutters>
            <v-col class="pt-2" cols="3">
              <label id="combobox-label">Size</label>
            </v-col>
            <v-col cols="9">
              <v-combobox
                id="select-line-width"
                aria-labelledby="combobox-label"
                :hide-details="true"
                :items="$_.keys(drawOptions)"
                outlined
                value="1"
                @input="value => updateFreeDrawingBrush({width: parseInt(value, 10)})"
              >
                <template #selection="{item}">
                  <span id="selected-line-width" class="sr-only">{{ item }} pixel line width</span>
                  <img aria-labelledby="selected-line-width" :src="drawOptions[item]" />
                </template>
                <template slot="item" slot-scope="data">
                  <span :id="`label-line-width-${data.item}`" class="sr-only">{{ data.item }} pixel line width</span>
                  <img :aria-labelledby="`label-line-width-${data.item}`" :src="drawOptions[data.item]" />
                </template>
              </v-combobox>
            </v-col>
          </v-row>
          <ColorPicker :set-fill="value => updateFreeDrawingBrush({color: value})" />
        </v-container>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import ColorPicker from '@/components/whiteboards/toolbar/ColorPicker'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'PencilBrushTool',
  components: {ColorPicker},
  mixins: [Whiteboarding],
  computed: {
    menu: {
      get() {
        return this.mode === 'draw'
      },
      set(value) {
        if (value) {
          this.setMode('draw')
          this.$putFocusNextTick('menu-header')
        }
        this.setDisableAll(value)
      }
    }
  },
  beforeDestroy() {
    this.setDisableAll(false)
  }
}
</script>
