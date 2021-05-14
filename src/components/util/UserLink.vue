<template>
  <span>
    <router-link v-if="!$isInIframe" :to="`/assets?userId=${user.id}`" class="hover-link">
      <font-awesome-icon
        v-if="user.isAdmin || user.isTeaching"
        icon="graduation-cap"
        class="ml-2"
      />
      {{ user.canvasFullName }}
    </router-link>
    <a
      v-if="$isInIframe"
      :href="`${$currentUser.course.assetLibraryUrl}#suitec_userId=${user.id}`"
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
    user: {
      required: true,
      type: Object
    }
  }
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
