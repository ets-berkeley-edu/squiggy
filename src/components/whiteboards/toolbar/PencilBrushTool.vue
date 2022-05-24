<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    @input="onMenuChange"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-draw-btn"
        :color="mode === 'draw' ? 'white' : 'primary'"
        icon
        :title="title"
        value="draw"
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">{{ title }}</span>
        <font-awesome-icon
          :color="{'white': mode === 'draw'}"
          icon="paintbrush"
          size="lg"
        />
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
                v-model="width"
                aria-labelledby="combobox-label"
                :hide-details="true"
                :items="$_.keys(drawOptions)"
                outlined
              >
                <template #selection="{item}">
                  <img
                    :alt="`${item} pixel line width`"
                    :aria-label="`${item} pixel line width`"
                    :src="drawOptions[item]"
                  />
                </template>
                <template #item="data">
                  <img
                    :alt="`${data.item} pixel line-width icon`"
                    :aria-label="`${data.item} pixel line-width icon`"
                    :src="drawOptions[data.item]"
                  />
                </template>
              </v-combobox>
            </v-col>
          </v-row>
          <ColorPicker
            :update-value="setColor"
            :value="color"
          />
        </v-container>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import ColorPicker from '@/components/whiteboards/toolbar/ColorPicker'
import constants from '@/store/whiteboarding/constants'
import Whiteboarding from '@/mixins/Whiteboarding'
import Vue from 'vue'

const DEFAULT_WIDTH = 1

export default {
  name: 'PencilBrushTool',
  components: {ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    color: undefined,
    drawOptions: undefined,
    menu: false,
    title: 'Draw colorful and squiggly lines',
    width: DEFAULT_WIDTH
  }),
  watch: {
    width(value) {
      if (value) {
        this.updateFreeDrawingBrush({width: parseInt(value, 10)})
      }
    }
  },
  created() {
    this.color = constants.COLORS.black.hex
    this.drawOptions = this.$_.clone(constants.DRAW_OPTIONS)
  },
  beforeDestroy() {
    this.setDisableAll(false)
  },
  methods: {
    onMenuChange(value) {
      if (value) {
        this.setColor(constants.COLORS.black.hex)
        this.setWidth(DEFAULT_WIDTH)
        this.updateFreeDrawingBrush({
          color: this.color,
          width: this.width
        })
        this.setMode('draw')
        this.$putFocusNextTick('menu-header')
      }
      this.setDisableAll(value)
    },
    setColor(value) {
      this.color = value
      this.updateFreeDrawingBrush({color: this.color})
    },
    setWidth(value) {
      this.width = parseInt(value, 10)
      this.updateFreeDrawingBrush({width: this.width})
    },
    updateFreeDrawingBrush(properties) {
      this.$_.assignIn(Vue.prototype.$canvas.freeDrawingBrush, properties)
    }
  }
}
</script>
