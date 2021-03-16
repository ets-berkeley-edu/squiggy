<template>
  <v-expand-transition>
    <v-alert
      v-if="messages.length"
      :id="id"
      aria-live="assertive"
      :icon="false"
      role="alert"
      :type="type"
      :width="width"
    >
      <div class="align-center d-flex">
        <div class="pr-4">
          <font-awesome-icon :icon="icon" size="2x" />
        </div>
        <div>
          <span v-if="messages.length === 1" :id="`${id}-0`">{{ messages[0] }}</span>
          <ul v-if="messages.length > 1">
            <li v-for="(error, index) in messages" :id="`${id}-${index}`" :key="index">{{ error }}</li>
          </ul>
        </div>
      </div>
    </v-alert>
  </v-expand-transition>
</template>

<script>
export default {
  name: 'Alert',
  props: {
    id: {
      required: true,
      type: String
    },
    messages: {
      required: true,
      type: Array
    },
    type: {
      default: 'warning',
      required: false,
      type: String
    },
    width: {
      default: 360,
      required: false,
      type: [Number, String]
    }
  },
  computed: {
    icon() {
      return this.type === 'error' || this.type === 'warning' ? 'exclamation-triangle' : 'info-circle'
    },
    show() {
      return !!this.messages.length
    }
  }
}
</script>
