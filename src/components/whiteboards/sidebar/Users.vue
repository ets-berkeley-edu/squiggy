<template>
  <v-menu
    id="collaborators-list"
    offset-y
    open-on-focus
    open-on-hover
  >
    <template #activator="{on, attrs}">
      <div
        id="show-whiteboard-collaborators-btn"
        :class="{'mx-2': !collapse}"
        tabindex="0"
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
          <v-avatar v-if="primary" color="green lighten-4" :size="collapse ? '36px' : '48px'">
            <img
              :id="`current-user-${primary.id}`"
              alt="Avatar"
              :src="getAvatar(primary)"
            />
          </v-avatar>
        </v-badge>
      </div>
    </template>
    <v-list>
      <v-list-item-title class="ma-3 pl-2">
        <h2 class="grey--text text--darken-2 title">Collaborator{{ whiteboard.users.length === 1 ? '' : 's' }}</h2>
      </v-list-item-title>
      <v-divider class="mb-2 mx-2" />
      <v-list-item v-for="user in usersOnline" :key="user.id">
        <v-list-item-avatar>
          <v-avatar color="green lighten-4" size="48px">
            <img
              :id="`user-${user.id}-online`"
              alt="Avatar"
              :src="getAvatar(user)"
            />
          </v-avatar>
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
        <v-list-item-content class="pl-2 my-2">
          <span class="font-weight-bold red--text">No one is active.</span>
        </v-list-item-content>
      </v-list-item>
      <v-list-item v-for="(user, index) in usersOffline" :key="user.id" :class="{'mb-1': index < usersOffline.length - 1}">
        <v-list-item-avatar>
          <v-avatar color="grey lighten-1" size="42px">
            <img
              :id="`user-${user.id}-offline`"
              alt="Avatar"
              :src="getAvatar(user)"
            >
          </v-avatar>
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
import Utils from '@/mixins/Utils.vue'
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Users',
  mixins: [Utils, Whiteboarding],
  props: {
    collapse: {
      required: true,
      type: Boolean
    }
  },
  data: () => ({
    primary: undefined
  }),
  created() {
    this.primary = this.usersOnline.length ? this.usersOnline[0] : this.$currentUser
  },
  methods: {
    getAvatar(user) {
      return user.canvasImage || require('@/assets/avatar-50.png')
    }
  }
}
</script>
