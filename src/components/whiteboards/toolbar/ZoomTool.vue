<template>
  <v-btn
    id="toolbar-fit-to-screen"
    class="mx-2"
    color="white"
    dense
    elevation="1"
    height="48px"
    rounded
    @click="toggleZoom"
  >
    <span class="sr-only">{{ fitToScreen ? 'Actual size' : 'Fit to screen' }}</span>
    <font-awesome-icon color="grey" :icon="fitToScreen ? 'search-plus' : 'search-minus'" size="2x" />
  </v-btn>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ZoomTool',
  mixins: [Whiteboarding]
}
</script>
