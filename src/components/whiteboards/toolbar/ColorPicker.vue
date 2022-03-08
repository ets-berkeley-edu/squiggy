<template>
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
      this.updateUnsavedFabricElement({key: 'fill', value})
    }
  }
}
</script>
