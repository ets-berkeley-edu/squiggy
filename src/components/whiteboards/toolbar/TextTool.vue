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
    <v-card width="360">
      <v-card-title class="sr-only">
        <h2 id="menu-header" class="sr-only">Select Text Size and Color</h2>
      </v-card-title>
      <v-card-text>
        <v-container class="pb-0 pt-5 text-body-1">
          <v-row class="pb-2" no-gutters>
            <v-col class="pt-1" cols="3">
              Size
            </v-col>
            <v-col class="pb-3" cols="9">
              <v-radio-group
                v-model="fontSize"
                class="mt-0 pl-1 pt-1"
                dense
                hide-details
                mandatory
              >
                <v-radio
                  v-for="option in textSizeOptions"
                  :id="`tool-select-text-size-${option.text.toLowerCase()}`"
                  :key="option.value"
                  :label="option.text"
                  :value="option.value"
                />
              </v-radio-group>
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
import ColorPicker from '@/components/whiteboards/toolbar/ColorPicker'
import constants from '@/store/whiteboarding/constants'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'TextTool',
  components: {ColorPicker},
  mixins: [Whiteboarding],
  data: () => ({
    fontSize: undefined,
    menu: false,
    textSizeOptions: undefined,
    tooltipText: 'Add text to your whiteboard'
  }),
  watch: {
    fontSize() {
      this.updateSelected({fontSize: this.fontSize})
    }
  },
  created() {
    this.textSizeOptions = this.$_.clone(constants.TEXT_SIZE_OPTIONS)
    this.fontSize = this.selected.fontSize
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
