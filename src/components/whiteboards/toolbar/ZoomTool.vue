<template>
  <v-btn
    id="toolbar-fit-to-screen"
    :class="{'white--text primary': mode === 'zoom'}"
    icon
    @click="toggleZoom"
  >
    <span class="sr-only">{{ fitToScreen ? 'Actual size' : 'Fit to screen' }}</span>
    <font-awesome-icon
      :color="mode === 'zoom' ? 'white' : 'grey'"
      :icon="fitToScreen ? 'search-plus' : 'search-minus'"
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
