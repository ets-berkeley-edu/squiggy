<template>
  <v-tooltip bottom :color="mode === 'move' ? 'primary' : undefined">
    <template #activator="{on, attrs}">
      <v-btn
        id="toolbar-move-btn"
        :color="mode === 'move' ? 'white' : 'primary'"
        icon
        :alt="tooltipText"
        value="move"
        v-bind="attrs"
        v-on="on"
      >
        <font-awesome-icon
          :color="{'white': mode === 'move'}"
          icon="arrows-up-down-left-right"
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
  name: 'MoveTool',
  mixins: [Whiteboarding],
  data: () => ({
    tooltipText: 'Move and transform whiteboard elements'
  })
}
</script>
