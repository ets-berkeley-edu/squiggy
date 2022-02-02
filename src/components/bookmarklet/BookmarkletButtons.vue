<template>
  <div class="d-flex">
    <div v-if="previousStep" class="pr-1">
      <v-btn
        id="go-previous-btn"
        @click="go(`/bookmarklet/popup/${previousStep}`)"
        @keypress.enter="go(`/bookmarklet/popup/${previousStep}`)"
      >
        Previous
      </v-btn>
    </div>
    <div v-if="nextStep" class="pr-1">
      <v-btn
        id="go-next-btn"
        @click="go(`/bookmarklet/popup/${nextStep}`)"
        @keypress.enter="go(`/bookmarklet/popup/${nextStep}`)"
      >
        Next
      </v-btn>
    </div>
    <div v-if="!nextStep" class="pr-1">
      <v-btn
        id="done-btn"
        @click="onClickDone"
        @keypress.enter="onClickDone"
      >
        Done
      </v-btn>
    </div>
    <div>
      <v-btn
        id="cancel-btn"
        @click="onClickCancel"
        @keypress.enter="onClickCancel"
      >
        Cancel
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
    onClickDone: {
      default: () => {
        this.closePopup()
      },
      required: false,
      type: Function
    },
    previousStep: {
      default: undefined,
      required: false,
      type: Number
    }
  },
  methods: {
    onClickCancel() {
      this.$announcer.polite('Canceled.')
      this.closePopup()
    }
  }
}
</script>
