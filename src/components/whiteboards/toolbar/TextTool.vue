<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-text-btn"
        :color="mode === 'text' ? 'white' : 'primary'"
        :disabled="disableAll"
        icon
        :title="title"
        value="text"
        v-bind="attrs"
        v-on="on"
      >
        <span class="sr-only">{{ title }}</span>
        <font-awesome-icon icon="font" size="lg" />
      </v-btn>
    </template>
    <v-card>
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Select Text Size and Color</h2>
      </v-card-title>
      <v-card-text>
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
                :items="textSizeOptions"
                :unclearable="true"
                :value="14"
                @input="value => updateSelected({fontSize: value})"
              />
            </v-col>
          </v-row>
          <ColorPicker :set-fill="value => updateSelected({fill: value})" />
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
  name: 'TextTool',
  components: {AccessibleSelect, ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    title: 'Add text to your whiteboard'
  }),
  computed: {
    menu: {
      get() {
        return this.mode === 'text'
      },
      set(value) {
        if (value) {
          this.setMode('text')
          this.$putFocusNextTick('menu-header')
        } else {
          this.resetSelected()
        }
        this.setDisableAll(value)
      }
    }
  },
  beforeDestroy() {
    this.setDisableAll(false)
  }
}
</script>
