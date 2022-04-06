<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    top
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-shapes"
        :disabled="disableAll"
        icon
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">Shapes</span>
        <font-awesome-icon icon="shapes" />
      </v-btn>
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
                  <span id="selected-shape" class="sr-only">{{ item }} shape</span>
                  <img aria-labelledby="selected-shape" :src="shapeOptions[item]" />
                </template>
                <template slot="item" slot-scope="data">
                  <span :id="`label-shape-${data.item}`" class="sr-only">{{ data.item }} shape</span>
                  <img :aria-labelledby="`label-shape-${data.item}`" :src="shapeOptions[data.item]" />
                </template>
              </v-combobox>
            </v-col>
          </v-row>
          <ColorPicker :set-fill="setColor" />
        </v-container>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import ColorPicker from '@/components/whiteboards/toolbar/ColorPicker'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ShapeToolDialog',
  components: {ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    shapeStyle: 'Rect:thin'
  }),
  computed: {
    menu: {
      get() {
        return this.mode === 'shape'
      },
      set(value) {
        this.resetSelected()
        if (value) {
          this.setMode('shape')
          this.setShapeStyle(this.shapeStyle)
          this.setColor(this.colors.black.hex)
          this.$putFocusNextTick('menu-header')
        }
        this.setDisableAll(value)
      }
    }
  },
  beforeDestroy() {
    this.setDisableAll(false)
  },
  methods: {
    getFill() {
      return this.selected.style === 'fill' ? this.selected.color : 'transparent'
    },
    setColor(value) {
      this.updateSelected({
        fill: this.getFill(),
        stroke: value,
      })
    },
    setShapeStyle(value) {
      const [shape, style] = value.split(':')
      this.updateSelected({
        fill: this.getFill(),
        shape,
        style,
        strokeWidth: style === 'thick' ? 10 : 2
      })
    }
  }
}
</script>
