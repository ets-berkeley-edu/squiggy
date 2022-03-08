<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-shapes"
        :disabled="disableAll"
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
      <v-card-text v-if="unsavedFabricElement">
        <v-container class="text-body-1">
          <v-row>
            <v-col cols="2">
              <div class="float-right pt-2">
                Shape
              </div>
            </v-col>
            <v-col cols="6">
              <v-combobox
                id="select-shape"
                aria-labelledby="label-select-shape"
                dense
                :hide-details="true"
                :items="$_.keys(options)"
                :value="unsavedFabricElement.shape"
                @input="setLineWidth"
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
        this.setUnsavedFabricElement(this.$_.cloneDeep(this.fabricElementTemplates.shape))
        this.$putFocusNextTick('menu-header')
      }
      this.setDisableAll(isOpen)
    }
  },
  beforeDestroy() {
    this.setDisableAll(false)
  },
  methods: {
    setFontSize(value) {
      this.updateUnsavedFabricElement({key: 'fontSize', value})
    }
  }
}
</script>
