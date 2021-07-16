<template>
  <div class="align-center d-flex flex-column mt-8 pt-10">
    <v-card
      v-if="!isLoading"
      class="elevation-1 w-50"
      outlined
    >
      <v-card-text class="pt-5 text-center">
        <PageTitle text="Launch failed" />
        <div
          id="launchfailure-alert-text"
          aria-live="polite"
          class="body-1 pt-5"
          role="alert"
        >
          <span id="launch-failure-message" aria-live="polite" role="alert">
            The SuiteC tools were unable to authenticate you during launch. This can happen if you have third-party cookies disabled in your
            browser.
          </span>
        </div>
        <div id="launchfailure-supplemental-text" class="body-1 pb-5 pt-5">
          <span v-if="isSafari">
            In Safari, go to Preferences &gt; Privacy and ensure that "Prevent cross-site tracking" and "Block all cookies" are <strong>not</strong> selected.
          </span>
          <span v-if="!isSafari">
            Please review your browser settings and ensure that you have enabled third-party cookies and/or cross-site tracking.
          </span>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import PageTitle from '@/components/util/PageTitle'

export default {
  name: 'LaunchFailure',
  components: {PageTitle},
  mixins: [Context],
  data: () => ({
    isSafari: window.navigator.userAgent.indexOf('Safari') !== -1 && window.navigator.userAgent.indexOf('Chrome') === -1
  }),
  mounted() {
    this.$ready('Launch Failure')
  }
}
</script>
