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
      <v-badge color="green" :content="String(sessions.length)">
        C<span class="sr-only">ollaborator{{ sessions.length === 1 ? '' : 's' }}</span>
      </v-badge>
    </div>
    <div v-if="!isMiniVariant" class="green py-5 text-center text-h6 white--text">
      <font-awesome-icon class="pr-3" icon="user" />
      {{ pluralize('collaborator', sessions.length) }}
    </div>
    <v-list class="w-100">
      <v-list-item v-for="session in sessions" :key="session.id">
        <v-list-item-avatar>
          <div class="d-flex">
            <div class="pr-3">
              <Avatar id="current-user-avatar" :user="session" />
            </div>
            <div class="green-text" :class="{'sr-only': isMiniVariant}">
              {{ session.canvasFullName }}<span v-if="session.id === $currentUser.id"> (me)</span>
              <span class="sr-only"> is online.</span>
            </div>
          </div>
        </v-list-item-avatar>
      </v-list-item>
      <v-list-item v-for="member in usersOffline" :key="member.id">
        <v-list-item-avatar>
          <div class="d-flex">
            <div class="pr-3">
              <Avatar id="current-user-avatar" :user="member" />
            </div>
            <div :class="{'sr-only': isMiniVariant}" class="grey-text">
              {{ member.canvasFullName }}<span v-if="member.id === $currentUser.id"> (me)</span>
              <span class="sr-only"> is not online.</span>
            </div>
          </div>
        </v-list-item-avatar>
      </v-list-item>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import Utils from '@/mixins/Utils.vue'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'OnlineUsers',
  mixins: [Utils, Whiteboarding],
  components: {Avatar},
  data: () => ({
    isMiniVariant: true
  }),
  computed: {
    usersOffline() {
      const onlineUserIds = this.$_.map(this.sessions, 'id')
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
