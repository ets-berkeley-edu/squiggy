<template>
  <v-btn
    id="toolbar-fit-to-screen"
    :color="mode === 'zoom' ? 'white' : 'primary'"
    icon
    value="zoom"
    @click="toggleZoom"
  >
    <span class="sr-only">{{ fitToScreen ? 'Actual size' : 'Fit to screen' }}</span>
    <font-awesome-icon
      :color="{'white': mode === 'zoom'}"
      :icon="fitToScreen ? 'search-plus' : 'search-minus'"
      size="lg"
    />
  </v-btn>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ZoomTool',
  mixins: [Whiteboarding]
}
</script>
