<template>
  <v-img
    :id="`user-avatar-${user.id}`"
    :class="`user-avatar-${size}`"
    :aria-label="`Photo of ${user.canvasFullName}`"
    :alt="`Photo of ${user.canvasFullName}`"
    :src="avatarUrl"
    class="avatar"
    @error="avatarError"
  />
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'Avatar',
  mixins: [Context],
  props: {
    size: {
      default: 'small',
      required: false,
      type: String
    },
    user: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    avatarUrl: undefined
  }),
  created() {
    this.avatarUrl = this.user.canvasImage || require('@/assets/avatar-50.png')
  },
  methods: {
    avatarError() {
      this.avatarUrl = require('@/assets/avatar-50.png')
    }
  }
}
</script>

<style scoped>
.avatar {
  background-image: url('~@/assets/avatar-50.png');
  background-size: cover;
  border: 5px solid #ccc;
  border-radius: 30px;
  height: 60px;
  object-fit: cover;
  width: 60px;
}
.user-avatar-large {
  border-radius: 75px;
  height: 150px;
  width: 150px;
}
.user-avatar-medium {
  border-radius: 50px;
  height: 100px;
  width: 100px;
}
.user-avatar-small {
  border: 1px;
  border-radius: 15px;
  height: 30px;
  padding: 2px 0 2px 0;
  width: 30px;
}
</style>
