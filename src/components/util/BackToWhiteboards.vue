<template>
  <div>
    <router-link v-slot="{navigate}" :to="linkBack()" custom>
      <v-btn
        id="whiteboards-btn"
        class="bg-transparent pl-0"
        :disabled="disabled"
        elevation="0"
        @click="navigate"
        @keypress.enter="navigate"
      >
        <font-awesome-icon class="mr-2" icon="less-than" size="sm" />
        Back to Whiteboards
      </v-btn>
    </router-link>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'BackToWhiteboards',
  mixins: [Utils],
  props: {
    anchor: {
      default: undefined,
      required: false,
      type: String
    },
    disabled: {
      required: false,
      type: Boolean
    }
  },
  methods: {
    linkBack() {
      return this.anchor ? `/whiteboards?anchor=${this.anchor}` : '/whiteboards'
    }
  }
}
</script>
