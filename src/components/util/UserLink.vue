<template>
  <span>
    <router-link
      v-if="!$isInIframe || !crossToolLink"
      :to="`/assets?userId=${user.id}`"
      :aria-label="screenreaderText"
      class="hover-link"
    >
      <font-awesome-icon
        v-if="user.isAdmin || user.isTeaching"
        icon="graduation-cap"
        class="ml-2"
      />
      {{ user.canvasFullName }}
    </router-link>
    <a
      v-if="$isInIframe && crossToolLink"
      :href="`${$currentUser.course.assetLibraryUrl}#suitec_userId=${user.id}`"
      :aria-label="screenreaderText"
      target="_parent"
      class="hover-link"
    >
      <font-awesome-icon
        v-if="user.isAdmin || user.isTeaching"
        icon="graduation-cap"
        class="ml-2"
      />
      {{ user.canvasFullName }}
    </a>
  </span>
</template>

<script>
export default {
  name: 'UserLink',
  props: {
    crossToolLink: {
      required: false,
      type: Boolean
    },
    user: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    screenreaderText: `View assets, filtered by ${this.user.isAdmin || this.user.isTeaching ? 'instructor' : 'user'} ${this.user.canvasFullName}`
  })
}
</script>

<style scoped>
.hover-link {
  text-decoration: none;
}

.hover-link:hover {
  text-decoration: underline;
}
</style>
