<template>
  <v-row no-gutters>
    <v-col class="pt-2" cols="3">
      Color
    </v-col>
    <v-col class="text-left" cols="9">
      <v-color-picker
        id="color-picker"
        hide-canvas
        hide-inputs
        hide-sliders
        show-swatches
        :swatches="swatches"
        :value="value"
        width="325"
        @input="updateValue"
      />
    </v-col>
  </v-row>
</template>

<script>
import constants from '@/store/whiteboarding/constants'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ColorPicker',
  mixins: [Whiteboarding],
  data: () => ({
    swatches: undefined
  }),
  props: {
    updateValue: {
      required: true,
      type: Function
    },
    value: {
      required: true,
      type: String
    }
  },
  created() {
    const colors = constants.COLORS
    this.swatches = [
      [colors.black.hex, colors.grey.hex],
      [colors.darkBlue.hex, colors.purple.hex],
      [colors.lightBlue.hex, colors.red.hex],
      [colors.green.hex, colors.yellow.hex],
      [colors.berkeleyBlue.hex, colors.californiaGold.hex]
    ]
  }
}
</script>
