<template>
  <v-menu
    id="collaborators-list"
    offset-y
    open-on-hover
  >
    <template #activator="{on, attrs}">
      <v-btn
        id="show-whiteboard-collaborators-btn"
        :class="{'mx-2': !collapse}"
        icon
        v-bind="attrs"
        v-on="on"
      >
        <v-badge
          bordered
          bottom
          :color="usersOnline.length ? 'green' : 'grey'"
          :content="usersOnline.length"
          :offset-x="collapse ? 20 : 10"
          :offset-y="collapse ? 20 : 10"
        >
          <v-avatar>
            <Avatar
              v-if="usersOnline.length"
              id="one-or-more-users-online"
              :size="collapse ? 'small' : 'medium'"
              :user="usersOnline[0]"
            />
            <Avatar
              v-if="!usersOnline.length"
              id="zero-users-online"
              :size="collapse ? 'small' : 'medium'"
              :user="$currentUser"
            />
          </v-avatar>
        </v-badge>
      </v-btn>
    </template>
    <v-list>
      <v-list-item v-for="user in usersOnline" :key="user.id">
        <v-list-item-avatar>
          <Avatar id="current-user-avatar" :user="user" />
        </v-list-item-avatar>
        <v-list-item-content>
          <span
            :id="`user-${user.id}-is-online`"
            class="font-weight-bold green--text"
          >
            {{ user.canvasFullName }}<span v-if="user.id === $currentUser.id"> (me)</span>
          </span>
          <span class="sr-only"> is online.</span>
        </v-list-item-content>
      </v-list-item>
      <v-list-item v-if="!usersOnline.length">
        <v-list-item-content class="pl-2 my-3">
          <span class="font-weight-bold red--text">No one is active.</span>
        </v-list-item-content>
      </v-list-item>
      <v-divider class="mb-2 mx-2" />
      <v-list-item v-for="(user, index) in usersOffline" :key="user.id" :class="{'mb-2': index < usersOffline.length - 1}">
        <v-list-item-avatar>
          <Avatar id="current-user-avatar" :user="user" />
        </v-list-item-avatar>
        <v-list-item-content>
          <span
            :id="`user-${user.id}-is-not-online`"
            class="grey--text"
          >
            {{ user.canvasFullName }}<span class="sr-only"> is not online.</span>
          </span>
        </v-list-item-content>
      </v-list-item>
    </v-list>
  </v-menu>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import Utils from '@/mixins/Utils.vue'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Users',
  mixins: [Utils, Whiteboarding],
  components: {Avatar},
  props: {
    collapse: {
      required: true,
      type: Boolean
    }
  }
}
</script>
