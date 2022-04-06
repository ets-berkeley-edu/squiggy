<template>
  <v-navigation-drawer
    absolute
    app
    class="navigation-drawer"
    permanent
    :right="true"
  >
    <!--
      :mini-variant="true"
      :clipped="$vuetify.breakpoint.lgAndUp"
      :expand-on-hover="true"
    -->
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
        Foo.
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
