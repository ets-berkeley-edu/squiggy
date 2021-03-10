<template>
  <div class="align-center d-flex flex-column mt-8 pt-10">
    <v-card
      v-if="!loading"
      class="elevation-1"
      outlined
    >
      <v-img
        v-if="!isInIframe"
        :aspect-ratio="16 / 9"
        src="@/assets/hello.jpg"
      />
      <v-card-text class="pt-5 text-center">
        <PageTitle text="Error" />
        <div
          id="error"
          aria-live="polite"
          class="body-1 pb-5 pt-2"
          role="alert"
        >
          <span id="error-message" aria-live="polite" role="alert">{{ message || 'Uh oh, there was a problem.' }}</span>
        </div>
        <div>
          Problem? Question?
          Email us at <a id="help-mailto" :href="`mailto:${$config.emailAddressSupport}`" target="_blank">{{ $config.emailAddressSupport }}</a>.
        </div>
        <div v-if="!isInIframe" class="pt-4">
          <v-btn id="return-home-btn" icon @click="$router.push('/', $_.noop)">
            <span class="sr-only">Go home</span>
            <font-awesome-icon icon="home" />
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Iframe from '@/mixins/Iframe'
import PageTitle from '@/components/util/PageTitle'

export default {
  name: 'Error',
  components: {PageTitle},
  mixins: [Context, Iframe],
  data: () => ({
    message: undefined
  }),
  mounted() {
    this.message = this.$route.query.m
    this.$ready('Error')
  }
}
</script>
