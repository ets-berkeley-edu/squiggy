<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    top
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-text"
        :disabled="disableAll"
        v-bind="attrs"
        value="text"
        v-on="on"
      >
        <span class="sr-only">Text</span>
        <font-awesome-icon icon="font" size="2x" />
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Select Text Size and Color</h2>
      </v-card-title>
      <v-card-text v-if="unsavedFabricElement">
        <v-container class="pb-0 pt-7 text-body-1">
          <v-row class="pb-2" no-gutters>
            <v-col class="pt-2" cols="3">
              Size
            </v-col>
            <v-col cols="9">
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
          <ColorPicker tool="text" />
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
  name: 'TextToolDialog',
  components: {AccessibleSelect, ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    menu: false
  }),
  watch: {
    menu(isOpen) {
      if (isOpen) {
        this.setMode('text')
        // this.setUnsavedFabricElement(this.$_.cloneDeep(this.fabricElementTemplates.text))
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
