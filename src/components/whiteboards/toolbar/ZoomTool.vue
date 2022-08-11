<template>
  <v-tooltip bottom :color="mode === 'zoom' ? 'primary' : undefined">
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-fit-to-screen"
        :alt="tooltipText"
        :color="mode === 'zoom' ? 'white' : 'primary'"
        icon
        value="zoom"
        v-bind="attrs"
        v-on="on"
        @click="fitToScreen"
      >
        <font-awesome-icon
          :color="{'white': mode === 'zoom'}"
          :icon="isFitToScreen ? 'search-plus' : 'search-minus'"
          size="lg"
        />
      </v-btn>
    </template>
    <span>{{ tooltipText }}</span>
  </v-tooltip>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ZoomTool',
  mixins: [Whiteboarding],
  computed: {
    tooltipText() {
      return this.fitToScreen ? 'Actual size' : 'Fit to screen'
    }
  }
}
</script>
