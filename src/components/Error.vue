<template>
  <div class="align-center d-flex flex-column mt-8 pt-10">
    <v-card
      v-if="!isLoading"
      class="elevation-1"
      outlined
    >
      <v-img
        v-if="!isInIframe"
        alt="TV screen with colored bars"
        aria-label="TV screen with colored bars"
        :aspect-ratio="16 / 9"
        src="@/assets/color-bars.png"
      />
      <v-card-text class="pt-5 text-center">
        <PageTitle text="Error" />
        <div
          id="error"
          aria-live="polite"
          class="body-1 pb-5 pt-2"
          role="alert"
        >
          <span
            id="error-message"
            aria-live="polite"
            role="alert"
            v-html="message || 'Uh oh, there was a problem.'"
          >
          </span>
        </div>
        <div>
          Problem? Question? Please review our <a id="help-article-kb" :href="servicePageUrl" target="_blank">support
            documentation</a> or Email us at <a
            id="help-mailto"
            :href="`mailto:${emailAddressSupport}`"
            target="_blank"
          >{{ emailAddressSupport }}</a>.
        </div>
        <div v-if="isInIframe" class="pt-4">
          <v-btn id="go-back-btn" icon @click="$router.go(-2)">
            Back
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import PageTitle from '@/components/util/PageTitle'

export default {
  name: 'Error',
  components: {PageTitle},
  mixins: [Context],
  data: () => ({
    emailAddressSupport: undefined,
    servicePageUrl: undefined,
    message: undefined
  }),
  created() {
    this.message = this.$route.query.m
    this.emailAddressSupport = this.$config.emailAddressSupport
    this.servicePageUrl = this.$config.servicePageUrl
    this.$ready('Error')
  }
}
</script>
