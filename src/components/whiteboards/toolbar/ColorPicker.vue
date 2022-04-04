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
        :swatches="[
          [colors.black.hex, colors.grey.hex],
          [colors.darkBlue.hex, colors.purple.hex],
          [colors.lightBlue.hex, colors.red.hex],
          [colors.green.hex, colors.yellow.hex]
        ]"
        :value="colors.black.hex"
        width="260"
        @input="setFill"
      />
    </v-col>
  </v-row>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ColorPicker',
  mixins: [Whiteboarding],
  props: {
    setFill: {
      required: true,
      type: Function
    }
  }
}
</script>
