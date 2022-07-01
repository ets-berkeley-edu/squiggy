<template>
  <a
    :id="`user-${user.id}-href`"
    :href="`${$currentUser.course.assetLibraryUrl}#suitec_userId=${user.id}`"
    :aria-label="`View assets, filtered by ${user.isAdmin || user.isTeaching ? 'instructor' : 'user'} ${user.canvasFullName}`"
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
  }
}
</script>
