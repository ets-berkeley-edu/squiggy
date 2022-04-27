<template>
  <v-btn
    id="toolbar-fit-to-screen"
    class="mx-2"
    :class="{'white--text primary': mode === 'zoom'}"
    dense
    elevation="1"
    height="48px"
    icon
    rounded
    value="zoom"
    width="55px"
    @click="toggleZoom"
  >
    <span class="sr-only">{{ fitToScreen ? 'Actual size' : 'Fit to screen' }}</span>
    <font-awesome-icon
      :color="mode === 'zoom' ? 'white' : 'grey'"
      :icon="fitToScreen ? 'search-plus' : 'search-minus'"
      size="2x"
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
