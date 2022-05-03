<template>
  <v-btn
    id="toolbar-move-btn"
    :color="mode === 'move' ? 'white' : 'primary'"
    icon
    :title="title"
    value="move"
  >
    <span class="sr-only">{{ title }}</span>
    <font-awesome-icon
      :color="{'white': mode === 'move'}"
      icon="arrows-up-down-left-right"
      size="lg"
    />
  </v-btn>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'MoveTool',
  mixins: [Whiteboarding],
  data: () => ({
    title: 'Move and transform whiteboard elements'
  })
}
</script>
