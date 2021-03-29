<template>
  <div class="align-center d-flex flex-column mt-8 pt-10">
    <v-card
      v-if="!isLoading"
      class="elevation-1"
      outlined
    >
      <v-img
        v-if="!$isInIframe"
        :aspect-ratio="16 / 9"
        src="@/assets/hello.jpg"
      />
      <v-card-text class="pt-5 text-center">
        <PageTitle text="Uh oh!" />
        <div
          id="page-not-found"
          aria-live="polite"
          class="body-1 pb-5 pt-2"
          role="alert"
        >
          Page not found.
        </div>
        <div>
          Problem? Question?
          Email us at <a id="help-mailto" :href="`mailto:${$config.emailAddressSupport}`" target="_blank">{{ $config.emailAddressSupport }}</a>.
        </div>
        <div v-if="!$isInIframe" class="pt-4">
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
  name: 'NotFound',
  components: {PageTitle},
  mixins: [Context, Iframe],
  mounted() {
    this.$ready('Page not found')
  }
}
</script>
