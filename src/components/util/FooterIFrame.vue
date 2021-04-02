<template>
  <v-footer id="footer">
    <v-container fluid class="pa-1">
      <v-row no-gutters justify="space-between">
        <v-col>
          <div>
            &copy; {{ new Date().getFullYear() }} Regents of the University of California. All Rights Reserved.
          </div>
          <div class="align-center d-flex">
            <div>
              <v-btn
                id="go-home-btn"
                :disabled="$router.currentRoute.meta.isLoginPage"
                icon
                @click="go('/')"
              >
                <span class="sr-only">Go home</span>
                <font-awesome-icon icon="home" size="lg" />
              </v-btn>
            </div>
            <div>
              <v-btn id="toggle-dark-mode-btn" icon @click="$vuetify.theme.dark = !$vuetify.theme.dark">
                <span class="sr-only">Turn dark mode {{ $vuetify.theme.dark ? 'off' : 'on' }}.</span>
                <font-awesome-icon :class="{'yellow--text': $vuetify.theme.dark}" :icon="$vuetify.theme.dark ? 'sun' : 'moon'" />
              </v-btn>
            </div>
            <div class="px-2">|</div>
            <div>
              <v-btn id="go-asset-library-btn" icon @click="go('/assets')">
                <span class="sr-only">Go to Asset Library</span>
                <font-awesome-icon icon="images" />
              </v-btn>
            </div>
            <div>
              <v-btn id="go-engagement-index-btn" icon @click="go('/engagement')">
                <span class="sr-only">Go to Engagement Index</span>
                <font-awesome-icon icon="list-ol" />
              </v-btn>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'FooterIFrame',
  mixins: [Context, Utils]
}
</script>
