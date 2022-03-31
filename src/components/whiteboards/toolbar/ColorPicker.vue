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
        value="red"
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
  data: () => ({
    swatches: [
      ['#000000', '#e6e6e6'],
      ['#5a6c7a', '#bc3aa7'],
      ['#0295de', '#af3837'],
      ['#0a8b00', '#bd8100']
    ]
  }),
  methods: {
    setFill(value) {
      console.log(`TODO: set fill to ${value}`)
    }
  }
}
</script>
