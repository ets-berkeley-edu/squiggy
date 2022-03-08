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
        <h2 id="menu-header" class="sr-only">Select Shape and Color</h2>
      </v-card-title>
      <v-card-text v-if="unsavedFabricElement">
        <v-container class="text-body-1">
          <v-row>
            <v-col cols="2">
              <div class="float-right pt-2">
                Size
              </div>
            </v-col>
            <v-col cols="6">
              <AccessibleSelect
                :dense="true"
                :hide-details="true"
                id-prefix="tool-select-text-size"
                :items="[
                  {text: 'Normal', value: 14},
                  {text: 'Title', value: 36}
                ]"
                :unclearable="true"
                :value="unsavedFabricElement.fontSize"
                @input="setFontSize"
              />
            </v-col>
          </v-row>
          <v-row>
            <v-col cols="2">
              <div class="float-right pt-2">
                Color
              </div>
            </v-col>
            <v-col cols="10">
              <div class="justify-start text-left">
                <v-color-picker
                  hide-canvas
                  hide-inputs
                  hide-sliders
                  show-swatches
                  :swatches="swatches"
                  :value="unsavedFabricElement.fill"
                  width="260"
                  @input="setFill"
                />
              </div>
            </v-col>
          </v-row>
        </v-container>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import Context from '@/mixins/Context'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ShapeToolDialog',
  components: {AccessibleSelect},
  mixins: [Context, Whiteboarding],
  data: () => ({
    menu: false,
    swatches: [['#000000', '#e6e6e6'], ['#5a6c7a', '#bc3aa7'], ['#0295de', '#af3837'], ['#0a8b00', '#bd8100']]
  }),
  watch: {
    menu(isOpen) {
      if (isOpen) {
        this.setUnsavedFabricElement(this.$_.cloneDeep(this.fabricElementTemplates.text))
        this.$putFocusNextTick('menu-header')
      }
      this.setDisableAll(isOpen)
    }
  },
  beforeDestroy() {
    this.setDisableAll(false)
  },
  methods: {
    setFill(value) {
      this.updateUnsavedFabricElement({key: 'fill', value})
    },
    setFontSize(value) {
      this.updateUnsavedFabricElement({key: 'fontSize', value})
    }
  }
}
</script>
