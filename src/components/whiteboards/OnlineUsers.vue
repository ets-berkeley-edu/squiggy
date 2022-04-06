<template>
  <v-navigation-drawer
    absolute
    app
    class="navigation-drawer"
    :clipped="$vuetify.breakpoint.lgAndUp"
    :expand-on-hover="true"
    :mini-variant="true"
    permanent
    :right="true"
  >
    <v-list>
      <v-list-item class="px-2">
        <v-list-item-avatar>
          <v-img src="https://randomuser.me/api/portraits/women/85.jpg"></v-img>
        </v-list-item-avatar>
      </v-list-item>

      <v-list-item link>
        <v-list-item-content>
          <v-list-item-title v-if="activeObject">
            {{ activeObject }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
    <div class="pa-2">
      <v-list-item>
        mode: {{ mode }}
      </v-list-item>
      <v-list-item>
        selected: {{ selected }}
      </v-list-item>
    </div>
  </v-navigation-drawer>
</template>

<script>
import Vue from 'vue'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'OnlineUsers',
  mixins: [Whiteboarding],
  computed: {
    activeObject: () => Vue.prototype.$canvas && Vue.prototype.$canvas.getActiveObject()
  }
}
</script>

<style scoped>
.navigation-drawer {
  z-index: 1100;
}
</style>
