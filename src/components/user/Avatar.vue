<template>
  <div class="position-relative">
    <v-img
      :class="`student-avatar-${size}`"
      :aria-label="`Photo of ${user.canvasFullName}`"
      :alt="`Photo of ${user.canvasFullName}`"
      :src="avatarUrl"
      class="avatar"
      @error="avatarError"
    />
  </div>
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
.student-avatar-large {
  border-radius: 75px;
  height: 150px;
  width: 150px;
}
.student-avatar-medium {
  border-radius: 50px;
  height: 100px;
  width: 100px;
}
.student-avatar-small {
  border: 1px;
  border-radius: 15px;
  height: 30px;
  padding: 2px 0 2px 0;
  width: 30px;
}
</style>
