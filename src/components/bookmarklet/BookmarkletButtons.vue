<template>
  <div class="d-flex">
    <div v-if="previousStep">
      <v-btn
        id="cancel-btn"
        @click="closePopup"
        @keypress.enter="closePopup"
      >
        Cancel
      </v-btn>
    </div>
    <div v-if="nextStep">
      <v-btn
        id="next-btn"
        @click="go(`/bookmarklet/popup/${nextStep}`)"
        @keypress.enter="go(`/bookmarklet/popup/${nextStep}`)"
      >
        Next
      </v-btn>
    </div>
    <div v-if="!nextStep">
      <v-btn
        id="done-btn"
        @click="done"
        @keypress.enter="done"
      >
        Next
      </v-btn>
    </div>
  </div>
</template>

<script>
import Bookmarklet from '@/mixins/Bookmarklet'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletButtons',
  mixins: [Bookmarklet, Utils],
  props: {
    currentStep: {
      required: true,
      type: Number
    },
    nextStep: {
      default: undefined,
      required: false,
      type: Number
    },
    previousStep: {
      default: undefined,
      required: false,
      type: Number
    }
  },
  methods: {
    done() {
      this.closePopup()
    }
  }
}
</script>
