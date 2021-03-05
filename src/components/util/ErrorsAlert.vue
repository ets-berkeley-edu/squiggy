<template>
  <v-alert
    aria-live="assertive"
    role="alert"
    type="error"
  >
    <span v-if="errors.length === 1">{{ errors[0] }}</span>
    <ul v-if="errors.length > 1">
      <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
    </ul>
  </v-alert>
</template>

<script>
export default {
  name: 'ErrorsAlert',
  props: {
    errors: {
      required: true,
      type: Array
    }
  },
  computed: {
    show() {
      return !!this.errors.length
    }
  }
}
</script>
