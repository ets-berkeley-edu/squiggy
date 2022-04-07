<template>
  <v-navigation-drawer
    absolute
    app
    class="navigation-drawer"
    :expand-on-hover="true"
    :mini-variant.sync="isMiniVariant"
    permanent
    :right="true"
  >
    <h2 :class="{'sr-only': isMiniVariant}">N collaborators</h2>
    <v-list>
      <v-list-item class="px-2">
        <v-list-item-avatar>
          <Avatar id="current-user-avatar" :user="$currentUser" />
        </v-list-item-avatar>
      </v-list-item>
      <v-list-item>
        <v-list-item-content>
          <v-list-item-title v-if="activeObject">
            {{ activeObject }}
          </v-list-item-title>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import Vue from 'vue'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'OnlineUsers',
  mixins: [Whiteboarding],
  components: {Avatar},
  data: () => ({
    isMiniVariant: true
  }),
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
