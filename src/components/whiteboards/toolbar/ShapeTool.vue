<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    @input="onMenuChange"
  >
    <template #activator="activator">
      <v-tooltip bottom :disabled="mode === 'shape'">
        <template #activator="tooltip">
          <v-btn
            id="toolbar-shapes"
            :alt="tooltipText"
            :color="mode === 'shape' ? 'white' : 'primary'"
            icon
            value="shape"
            v-bind="activator.attrs"
            v-on="{...activator.on, ...tooltip.on}"
          >
            <font-awesome-icon
              :color="{'white': mode === 'shape'}"
              icon="shapes"
              size="lg"
            />
          </v-btn>
        </template>
        <span>{{ tooltipText }}</span>
      </v-tooltip>
    </template>
    <v-card>
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Select shape and color</h2>
      </v-card-title>
      <v-card-text>
        <v-container class="pb-0 pt-7 text-body-1">
          <v-row class="pb-2" no-gutters>
            <v-col class="pt-2" cols="3">
              <label id="combobox-label">Shape</label>
            </v-col>
            <v-col cols="9">
              <v-combobox
                id="select-shape"
                aria-labelledby="combobox-label"
                :hide-details="true"
                :items="$_.keys(shapeOptions)"
                outlined
                :value="shapeStyle"
                @input="setShapeStyle"
              >
                <template #selection="{item}">
                  <img
                    :alt="`${item} shape`"
                    :aria-label="`${item} shape`"
                    :src="shapeOptions[item]"
                  />
                </template>
                <template #item="data">
                  <img
                    :alt="`${data.item} shape`"
                    :aria-label="`${data.item} shape`"
                    :src="shapeOptions[data.item]"
                  />
                </template>
              </v-combobox>
            </v-col>
          </v-row>
          <ColorPicker
            :update-value="setColor"
            :value="selected.color"
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

export default {
  name: 'ShapeTool',
  components: {ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    color: undefined,
    menu: false,
    shapeOptions: undefined,
    shapeStyle: undefined,
    tooltipText: 'Add shapes to your whiteboard'
  }),
  created() {
    this.shapeOptions = this.$_.clone(constants.SHAPE_OPTIONS)
  },
  beforeDestroy() {
    this.setDisableAll(false)
  },
  methods: {
    calculateFill() {
      return this.shapeStyle.includes('fill') ? this.color : 'transparent'
    },
    onMenuChange(value) {
      if (value) {
        this.resetSelected()
        this.setMode('shape')
        this.color = constants.COLORS.black.hex
        this.shapeStyle = 'Rect:thin'
        this.updateSelected({fill: this.calculateFill()})
        this.$putFocusNextTick('menu-header')
      }
      this.setDisableAll(value)
    },
    setColor(value) {
      this.color = value
      this.updateSelected({
        color: this.color,
        fill: this.calculateFill(),
        stroke: this.color
      })
    },
    setShapeStyle(value) {
      this.shapeStyle = value
      const [shape, style] = value.split(':')
      this.updateSelected({
        fill: this.calculateFill(),
        shape,
        strokeWidth: style === 'thick' ? 10 : 2,
        style
      })
    }
  }
}
</script>
