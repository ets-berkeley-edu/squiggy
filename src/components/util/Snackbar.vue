<template>
  <v-snackbar
    v-model="snackbar"
    :color="color"
    rounded
    :timeout="timeout"
    :top="top"
  >
    <div class="d-flex align-center justify-space-between">
      <div
        id="alert-text"
        aria-live="polite"
        class="ml-4 mr-4 title"
        role="alert"
      >
        <slot />
      </div>
      <div>
        <v-btn
          id="close-alert-btn"
          icon
          @click="() => snackbar = false"
        >
          <span class="sr-only">Close</span>
          <font-awesome-icon icon="x" />
        </v-btn>
      </div>
    </div>
  </v-snackbar>
</template>

<script>
import Context from '@/mixins/Context'

export default {
  name: 'Snackbar',
  mixins: [Context],
  props: {
    color: {
      default: 'primary',
      required: false,
      type: String
    },
    timeout: {
      default: 3000,
      required: false,
      type: Number
    },
    top: {
      required: false,
      type: Boolean
    }
  },
  data: () => ({
    snackbar: true
  })
}
</script>
