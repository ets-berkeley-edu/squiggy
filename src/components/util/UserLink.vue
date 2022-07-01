<template>
  <span>
    <router-link
      v-if="!$isInIframe || !crossToolLink"
      :id="`user-${user.id}-href`"
      :to="`/assets?userId=${user.id}`"
      :aria-label="`View assets, filtered by ${user.isAdmin || user.isTeaching ? 'instructor' : 'user'} ${user.canvasFullName}`"
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
    crossToolLink: {
      required: false,
      type: Boolean
    },
    user: {
      required: true,
      type: Object
    }
  }
}
</script>
