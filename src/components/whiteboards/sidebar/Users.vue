<template>
  <v-navigation-drawer
    app
    class="navigation-drawer"
    :expand-on-hover="true"
    :mini-variant.sync="isMiniVariant"
    right
  >
    <div v-if="isMiniVariant" class="pt-5 text-center">
      <v-badge color="green" :content="String(usersOnline.length)">
        C<span class="sr-only">ollaborator{{ usersOnline.length === 1 ? '' : 's' }}</span>
      </v-badge>
    </div>
    <div v-if="!isMiniVariant" class="green py-5 text-center text-h6 white--text">
      <font-awesome-icon class="pr-3" icon="user" />
      {{ pluralize('collaborator', usersOnline.length) }}
    </div>
    <v-list>
      <v-list-item v-for="user in usersOnline" :key="user.id">
        <v-list-item-avatar :class="{'pr-3': isMiniVariant}">
          <Avatar id="current-user-avatar" :user="user" />
        </v-list-item-avatar>
        <v-list-item-content :class="{'sr-only': isMiniVariant}">
          <span :id="`user-${user.id}-is-online`" class="font-weight-bold green--text">{{ user.canvasFullName }}<span v-if="user.id === $currentUser.id"> (me)</span></span>
          <span class="sr-only"> is online.</span>
        </v-list-item-content>
      </v-list-item>
      <v-list-item v-if="!usersOnline.length">
        <v-list-item-content v-if="isMiniVariant" class="pl-1">
          &mdash;
        </v-list-item-content>
        <v-list-item-content v-if="!isMiniVariant" class="pl-2 my-3">
          <span class="font-weight-bold red--text">No one is active.</span>
        </v-list-item-content>
      </v-list-item>
      <v-divider class="mb-8 mx-2" />
      <v-list-item v-for="user in usersOffline" :key="user.id" class="mb-2">
        <v-list-item-avatar :class="{'pr-3': isMiniVariant}">
          <Avatar id="current-user-avatar" :user="user" />
        </v-list-item-avatar>
        <v-list-item-content :class="{'sr-only': isMiniVariant}">
          <span :id="`user-${user.id}-is-not-online`" class="grey--text">{{ user.canvasFullName }}<span class="sr-only"> is not online.</span></span>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import Utils from '@/mixins/Utils.vue'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Users',
  mixins: [Utils, Whiteboarding],
  components: {Avatar},
  data: () => ({
    isMiniVariant: true
  }),
  computed: {
    usersOffline() {
      return this.$_.filter(this.whiteboard.users, user => !user.isOnline)
    },
    usersOnline() {
      return this.$_.filter(this.whiteboard.users, user => user.isOnline)
    }
  }
}
</script>

<style scoped>
.navigation-drawer {
  z-index: 1100;
}
</style>
