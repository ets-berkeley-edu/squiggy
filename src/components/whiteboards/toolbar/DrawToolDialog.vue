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
          <ColorPicker tool="draw" />
        </v-container>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import ColorPicker from '@/components/whiteboards/toolbar/ColorPicker'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'DrawToolDialog',
  components: {AccessibleSelect, ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    menu: false
  }),
  watch: {
    menu(isOpen) {
      if (isOpen) {
        this.setUnsavedFabricElement(this.$_.cloneDeep(this.fabricElementTemplates.paint))
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
