<template>
  <v-expand-transition>
    <v-alert
      v-if="errors.length"
      aria-live="assertive"
      role="alert"
      type="error"
      :width="width"
    >
      <span v-if="errors.length === 1">{{ errors[0] }}</span>
      <ul v-if="errors.length > 1">
        <li v-for="(error, index) in errors" :key="index">{{ error }}</li>
      </ul>
    </v-alert>
  </v-expand-transition>
</template>

<script>
export default {
  name: 'ErrorsAlert',
  props: {
    errors: {
      required: true,
      type: Array
    },
    width: {
      default: 360,
      required: false,
      type: Number
    }
  },
  computed: {
    show() {
      return !!this.errors.length
    }
  }
}
</script>
