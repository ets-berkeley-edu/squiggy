<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-draw"
        :disabled="disableAll"
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">Draw</span>
        <font-awesome-icon icon="paintbrush" size="2x" />
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Select brush and color</h2>
      </v-card-title>
      <v-card-text v-if="unsavedFabricElement">
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
                :items="$_.keys(options)"
                outlined
                :value="unsavedFabricElement.lineWidth"
                @input="setLineWidth"
              >
                <template #selection="{item}">
                  <span id="selected-line-width" class="sr-only">{{ item }} pixel line width</span>
                  <img aria-labelledby="selected-line-width" :src="options[item]" />
                </template>
                <template slot="item" slot-scope="data">
                  <span :id="`label-line-width-${data.item}`" class="sr-only">{{ data.item }} pixel line width</span>
                  <img :aria-labelledby="`label-line-width-${data.item}`" :src="options[data.item]" />
                </template>
              </v-combobox>
            </v-col>
          </v-row>
          <ColorPicker tool="draw" />
        </v-container>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import ColorPicker from '@/components/whiteboards/toolbar/ColorPicker'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'DrawToolDialog',
  components: {ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    menu: false,
    options: {
      1: require('@/assets/whiteboard/draw-small.png'),
      5: require('@/assets/whiteboard/draw-medium.png'),
      10: require('@/assets/whiteboard/draw-large.png')
    }
  }),
  watch: {
    menu(isOpen) {
      if (isOpen) {
        this.setUnsavedFabricElement(this.$_.cloneDeep(this.fabricElementTemplates.draw))
        this.$putFocusNextTick('menu-header')
      }
      this.setDisableAll(isOpen)
    }
  },
  beforeDestroy() {
    this.setDisableAll(false)
  },
  methods: {
    setLineWidth(value) {
      this.updateUnsavedFabricElement({key: 'lineWidth', value})
    }
  }
}
</script>
