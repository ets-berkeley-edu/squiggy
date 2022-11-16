<template>
  <a
    :id="`user-${user.id}-href`"
    :href="destination"
    :aria-label="ariaLabel"
    target="_parent"
    class="hover-link"
  >
    <font-awesome-icon
      v-if="user.isAdmin || user.isTeaching"
      :id="`user-${user.id}-graduation-cap`"
      icon="graduation-cap"
      class="ml-2"
    />
    {{ user.canvasFullName }}
  </a>
</template>

<script>
export default {
  name: 'CrossToolUserLink',
  props: {
    user: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    ariaLabel: null,
    destination: null
  }),
  created() {
    if (this.$currentUser.impactStudioUrl) {
      this.destination = `${this.$currentUser.impactStudioUrl}#suitec_userId=${this.user.id}`
      this.ariaLabel = `View Impact Studio profile for ${this.user.canvasFullName}`
    } else {
      this.destination = `${this.$currentUser.assetLibraryUrl}#suitec_userId=${this.user.id}`
      this.ariaLabel = `View assets, filtered by ${this.user.isAdmin || this.user.isTeaching ? 'instructor' : 'user'} ${this.user.canvasFullName}`
    }
  }
}
</script>
