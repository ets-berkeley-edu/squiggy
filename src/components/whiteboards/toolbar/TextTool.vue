<template>
  <v-menu
    v-model="menu"
    :close-on-content-click="false"
    offset-y
    @input="onMenuChange"
  >
    <template #activator="activator">
      <v-tooltip bottom :disabled="mode === 'text'">
        <template #activator="tooltip">
          <v-btn
            id="toolbar-text-btn"
            :alt="tooltipText"
            :color="mode === 'text' ? 'white' : 'primary'"
            icon
            value="text"
            v-bind="activator.attrs"
            v-on="{...activator.on, ...tooltip.on}"
          >
            <font-awesome-icon
              :color="{'white': mode === 'text'}"
              icon="font"
              size="lg"
            />
          </v-btn>
        </template>
        <span>{{ tooltipText }}</span>
      </v-tooltip>
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
                :key="menu"
                :dense="true"
                :hide-details="true"
                id-prefix="tool-select-text-size"
                :items="textSizeOptions"
                :unclearable="true"
                :value="selected.fontSize"
                @input="fontSize => updateSelected({fontSize})"
              />
            </v-col>
          </v-row>
          <ColorPicker
            :update-value="fill => updateSelected({fill})"
            :value="selected.fill"
          />
        </v-container>
      </v-card-text>
    </v-card>
  </v-menu>
</template>

<script>
import AccessibleSelect from '@/components/util/AccessibleSelect'
import ColorPicker from '@/components/whiteboards/toolbar/ColorPicker'
import constants from '@/store/whiteboarding/constants'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'TextTool',
  components: {AccessibleSelect, ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    menu: false,
    textSizeOptions: undefined,
    tooltipText: 'Add text to your whiteboard'
  }),
  created() {
    this.textSizeOptions = this.$_.clone(constants.TEXT_SIZE_OPTIONS)
  },
  beforeDestroy() {
    this.setDisableAll(false)
  },
  methods: {
    onMenuChange(value) {
      if (value) {
        this.resetSelected()
        this.textSizeOptions = this.$_.clone(constants.TEXT_SIZE_OPTIONS)
        this.setMode('text')
        this.$putFocusNextTick('menu-header')
      }
      this.setDisableAll(value)
    }
  }
}
</script>
