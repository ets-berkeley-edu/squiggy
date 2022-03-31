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
                :items="$_.keys(options)"
                outlined
                value="circle"
                @input="setShape"
              >
                <template #selection="{item}">
                  <span id="selected-shape" class="sr-only">{{ item }} shape</span>
                  <img aria-labelledby="selected-shape" :src="options[item]" />
                </template>
                <template slot="item" slot-scope="data">
                  <span :id="`label-shape-${data.item}`" class="sr-only">{{ data.item }} shape</span>
                  <img :aria-labelledby="`label-shape-${data.item}`" :src="options[data.item]" />
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
  name: 'ShapeToolDialog',
  components: {ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    menu: false,
    options: {
      'Rect:thin': require('@/assets/whiteboard/shape-rect-thin.png'),
      'Rect:thick': require('@/assets/whiteboard/shape-rect-thick.png'),
      'Rect:fill': require('@/assets/whiteboard/shape-rect-fill.png'),
      'Circle:thin': require('@/assets/whiteboard/shape-circle-thin.png'),
      'Circle:thick': require('@/assets/whiteboard/shape-circle-thick.png'),
      'Circle:fill': require('@/assets/whiteboard/shape-circle-fill.png')
    }
  }),
  watch: {
    menu(isOpen) {
      if (isOpen) {
        this.$putFocusNextTick('menu-header')
      }
      this.setDisableAll(isOpen)
    }
  },
  beforeDestroy() {
    this.setDisableAll(false)
  },
  methods: {
    setShape(value) {
      console.log(`TODO: set shape to ${value}`)
    }
  }
}
</script>
