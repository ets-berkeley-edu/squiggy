<template>
  <v-btn
    id="toolbar-move-btn"
    class="pr-2"
    :disabled="disableAll || mode === 'move'"
    icon
    value="move"
    width="55px"
  >
    <span class="sr-only">Move and transform</span>
    <font-awesome-icon
      :color="mode === 'move' ? 'white' : 'grey'"
      icon="arrows-up-down-left-right"
      size="2x"
    />
  </v-btn>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'MoveTool',
  mixins: [Whiteboarding]
}
</script>
