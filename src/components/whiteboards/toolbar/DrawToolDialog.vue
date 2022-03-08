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
        <font-awesome-icon icon="paintbrush" />
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Select brush and color</h2>
      </v-card-title>
      <v-card-text v-if="unsavedFabricElement">
        <v-container class="text-body-1">
          <v-row>
            <v-col cols="2">
              <div id="label-select-line-width" class="float-right pt-2">
                Size
              </div>
            </v-col>
            <v-col cols="6">
              <v-combobox
                id="select-line-width"
                aria-labelledby="label-select-line-width"
                dense
                :hide-details="true"
                :items="$_.keys(options)"
                :value="unsavedFabricElement.shape"
                @input="setShape"
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
    setShape(value) {
      this.updateUnsavedFabricElement({key: 'shape', value})
    }
  }
}
</script>
