<template>
  <v-card
    class="mx-auto transparent"
    elevation="0"
    style="margin-top: -64px;"
  >
    <v-toolbar
      bottom
      color="transparent"
      dense
      elevation="0"
    >
      <ZoomTool />
      <SettingsTool v-if="$currentUser.isAdmin || $currentUser.isTeaching" />
    </v-toolbar>
  </v-card>
</template>

<script>
import SettingsTool from '@/components/whiteboards/toolbar/SettingsTool'
import Whiteboarding from '@/mixins/Whiteboarding'
import ZoomTool from '@/components/whiteboards/toolbar/ZoomTool'

export default {
  name: 'ToolbarReadOnly',
  mixins: [Whiteboarding],
  components: {SettingsTool, ZoomTool}
}
</script>
