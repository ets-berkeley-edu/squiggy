<template>
  <span>
    <router-link
      v-if="!$isInIframe || !crossToolLink"
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
    <CrossToolUserLink v-if="$isInIframe && crossToolLink" :user="user" />
  </span>
</template>

<script>
import CrossToolUserLink from '@/components/util/CrossToolUserLink'

export default {
  name: 'UserLink',
  components: {CrossToolUserLink},
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
    if (this.$currentUser.course.impactStudioUrl) {
      if (this.source === 'impactstudio') {
        this.destination = `/profile/user/${this.user.id}`
        this.ariaLabel = `View Impact Studio profile for ${this.user.canvasFullName}`
      } else {
        this.crossToolLink = true
      }
    } else {
      if (this.source === 'assetlibrary') {
        this.destination = `/assets?userId=${this.user.id}`
        this.ariaLabel = `View assets, filtered by ${this.user.isAdmin || this.user.isTeaching ? 'instructor' : 'user'} ${this.user.canvasFullName}`
      } else {
        this.crossToolLink = true
      }
    }
  }
}
</script>
