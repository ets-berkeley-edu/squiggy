<template>
  <v-btn
    id="toolbar-move-btn"
    class="pr-2"
    :disabled="disableAll || mode === 'move'"
    icon
    :title="title"
    value="move"
    width="55px"
  >
    <span class="sr-only">{{ title }}</span>
    <font-awesome-icon
      :color="mode === 'move' ? 'white' : 'grey'"
      icon="arrows-up-down-left-right"
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
