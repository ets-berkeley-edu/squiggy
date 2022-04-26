<template>
  <v-card
    class="mx-auto transparent"
    elevation="0"
    style="margin-top: -64px;"
    max-width="700px"
  >
    <v-toolbar
      bottom
      color="transparent"
      dense
      elevation="0"
    >
      <ZoomTool />
    </v-toolbar>
  </v-card>
</template>

<script>
import ZoomTool from '@/components/whiteboards/toolbar/ZoomTool'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'ToolbarReadOnly',
  mixins: [Whiteboarding],
  components: {ZoomTool}
}
</script>
