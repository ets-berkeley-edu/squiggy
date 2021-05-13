<template>
  <router-link :to="`/assets?userId=${user.id}`" class="hover-link">
    <font-awesome-icon
      v-if="user.isAdmin || user.isTeaching"
      icon="graduation-cap"
      class="leaderboard-cap"
    />
    {{ user.canvasFullName }}
  </router-link>
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
