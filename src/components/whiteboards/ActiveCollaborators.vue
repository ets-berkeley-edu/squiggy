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
    <div v-if="isMiniVariant" class="pt-5 text-center">
      <v-badge color="green" :content="String(activeCollaborators.length)">
        C<span class="sr-only">ollaborator{{ activeCollaborators.length === 1 ? '' : 's' }}</span>
      </v-badge>
    </div>
    <div v-if="!isMiniVariant" class="green py-5 text-center text-h6 white--text">
      <font-awesome-icon class="pr-3" icon="user" />
      {{ pluralize('collaborator', activeCollaborators.length) }}
    </div>
    <v-list>
      <v-list-item v-for="collaborator in activeCollaborators" :key="collaborator.id">
        <v-list-item-avatar :class="{'pr-3': isMiniVariant}">
          <Avatar id="current-user-avatar" :user="collaborator" />
        </v-list-item-avatar>
        <v-list-item-content :class="{'sr-only': isMiniVariant}">
          <span class="font-weight-bold green--text">{{ collaborator.canvasFullName }}<span v-if="collaborator.id === $currentUser.id"> (me)</span></span>
          <span class="sr-only"> is online.</span>
        </v-list-item-content>
      </v-list-item>
      <v-list-item v-if="!activeCollaborators.length">
        <v-list-item-content v-if="isMiniVariant" class="pl-1">
          &mdash;
        </v-list-item-content>
        <v-list-item-content v-if="!isMiniVariant" class="pl-2">
          <span class="font-weight-bold red--text">No one is active.</span>
        </v-list-item-content>
      </v-list-item>
      <v-divider class="mx-2" />
      <v-list-item v-for="member in usersOffline" :key="member.id">
        <v-list-item-avatar :class="{'pr-3': isMiniVariant}">
          <Avatar id="current-user-avatar" :user="member" />
        </v-list-item-avatar>
        <v-list-item-content :class="{'sr-only': isMiniVariant}">
          <span class="grey--text">{{ member.canvasFullName }}<span class="sr-only"> is not online.</span></span>
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
  name: 'ActiveCollaborators',
  mixins: [Utils, Whiteboarding],
  components: {Avatar},
  data: () => ({
    isMiniVariant: true
  }),
  computed: {
    usersOffline() {
      const onlineUserIds = this.$_.map(this.activeCollaborators, 'id')
      return this.$_.filter(this.whiteboard.users, user => !onlineUserIds.includes(user.id))
    }
  }
}
</script>

<style scoped>
.navigation-drawer {
  z-index: 1100;
}
</style>
