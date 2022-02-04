<template>
  <v-footer id="footer" app>
    <div class="d-flex justify-space-between w-100">
      <div class="align-center d-flex">
        <div>
          <DarkModeToggle />
        </div>
        <div class="font-size-12">
          &copy; {{ new Date().getFullYear() }} The Regents of the University of California
        </div>
      </div>
      <div class="py-2">
        <div class="d-flex">
          <div v-if="previousStep" class="pr-2">
            <v-btn
              id="go-previous-btn"
              :disabled="isSaving"
              @click="goToPrevious"
              @keypress.enter="goToPrevious"
            >
              <font-awesome-icon class="mr-3" icon="arrow-left" />
              Previous<span class="sr-only"> step</span>
            </v-btn>
          </div>
          <div v-if="nextStep" class="pr-2">
            <v-btn
              id="go-next-btn"
              color="primary"
              :disabled="disableNext || isSaving"
              @click="goToNext"
              @keypress.enter="goToNext"
            >
              Next<span class="sr-only"> step</span>
              <font-awesome-icon class="ml-3" icon="arrow-right" />
            </v-btn>
          </div>
          <div v-if="isAuthorized && !nextStep" class="pr-2">
            <v-btn
              id="done-btn"
              color="primary"
              :disabled="disableSave || isSaving"
              @click="onClickSave"
              @keypress.enter="onClickSave"
            >
              <font-awesome-icon class="mr-2" icon="check" />
              Save<span class="sr-only"> asset(s) to SuiteC</span>
            </v-btn>
          </div>
          <div>
            <v-btn
              :id="isAuthorized ? 'cancel-btn' : 'close-btn'"
              :disabled="isSaving"
              text
              @click="onClickCancel"
              @keypress.enter="onClickCancel"
            >
              {{ isAuthorized ? 'Cancel' : 'Close' }}
            </v-btn>
          </div>
        </div>
      </div>
    </div>
  </v-footer>
</template>

<script>
import Bookmarklet from '@/mixins/Bookmarklet'
import DarkModeToggle from '@/components/util/DarkModeToggle'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletButtons',
  mixins: [Bookmarklet, Utils],
  components: {DarkModeToggle},
  props: {
    disableNext: {
      required: false,
      type: Boolean
    },
    disableSave: {
      required: false,
      type: Boolean
    },
    isSaving: {
      required: false,
      type: Boolean
    },
    nextStep: {
      default: undefined,
      required: false,
      type: Number
    },
    onClickSave: {
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
    goToNext() {
      this.$announcer.polite('Going to next step')
      this.go(`/bookmarklet/popup/${this.nextStep}`)
    },
    goToPrevious() {
      this.$announcer.polite('Going to previous step')
      this.go(`/bookmarklet/popup/${this.previousStep}`)
    },
    onClickCancel() {
      this.$announcer.polite('Canceled.')
      this.closePopup()
    }
  }
}
</script>
