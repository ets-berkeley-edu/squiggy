<template>
  <span>
    <router-link
      v-if="!crossToolLink"
      :id="`user-${user.id}-href`"
      :to="destination"
      :aria-label="ariaLabel"
      class="hover-link"
    >
      <font-awesome-icon
        v-if="user.isAdmin || user.isTeaching"
        icon="graduation-cap"
        class="ml-2"
      />
      {{ user.canvasFullName }}
    </router-link>
    <CrossToolUserLink v-if="crossToolLink" :user="user" />
    <v-btn
      v-if="user.lookingForCollaborators && user.id !== $currentUser.id"
      color="success"
      x-small
      @click="startCanvasConversation(user)"
      @keypress.enter.prevent="startCanvasConversation(user)"
    >
      <v-icon small>mdi-account-plus</v-icon><span class="sr-only">Start a conversation</span>
    </v-btn>
  </span>
</template>

<script>
import CanvasConversation from '@/mixins/CanvasConversation'
import CrossToolUserLink from '@/components/util/CrossToolUserLink'

export default {
  name: 'UserLink',
  components: {CrossToolUserLink},
  mixins: [CanvasConversation],
  props: {
    source: {
      required: true,
      type: String
    },
    user: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    ariaLabel: null,
    crossToolLink: false,
    destination: null
  }),
  created() {
    if (this.source === 'assetlibrary') {
      this.destination = `/assets?userId=${this.user.id}`
      this.ariaLabel = `View assets, filtered by ${this.user.isAdmin || this.user.isTeaching ? 'instructor' : 'user'} ${this.user.canvasFullName}`
    }
    else if (this.$currentUser.impactStudioUrl) {
      if (this.source === 'impactstudio') {
        this.destination = `/profile/user/${this.user.id}`
        this.ariaLabel = `View Impact Studio profile for ${this.user.canvasFullName}`
      } else {
        this.crossToolLink = true
      }
    } else {
      this.crossToolLink = true
    }
  }
}
</script>
