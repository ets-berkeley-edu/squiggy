<template>
  <v-footer
    id="footer"
    app
  >
    <v-container fluid class="pa-1">
      <v-row no-gutters justify="space-between">
        <v-col>
          <div v-if="isInIframe || !$currentUser.isAuthenticated">
            &copy; {{ new Date().getFullYear() }} Regents of the University of California. All Rights Reserved.
          </div>
          <div v-if="!isInIframe && $currentUser.isAuthenticated" class="d-flex">
            <div>
              <v-btn icon @click="go('/')">
                <span class="sr-only">Go home</span>
                <font-awesome-icon icon="home" />
              </v-btn>
            </div>
            <div>
              <v-btn icon @click="go('/assets')">
                <span class="sr-only">Go to Asset Library</span>
                <font-awesome-icon icon="images" />
              </v-btn>
            </div>
            <div>
              <v-btn icon @click="go('/engagement')">
                <span class="sr-only">Go to Engagement Index</span>
                <font-awesome-icon icon="list-ol" />
              </v-btn>
            </div>
          </div>
        </v-col>
        <v-col v-if="!isInIframe">
          <div class="float-right">
            <div class="align-center d-flex">
              <div>
                {{ $_.get($announcer, 'data.content') }}
              </div>
              <div v-if="$currentUser.isAuthenticated" class="pl-2">
                |
              </div>
              <div v-if="$currentUser.isAuthenticated">
                <v-btn icon @click="logOut">
                  <span class="sr-only">Log Out</span>
                  <font-awesome-icon icon="sign-out-alt" />
                </v-btn>
              </div>
            </div>
          </div>
        </v-col>
      </v-row>
    </v-container>
  </v-footer>
</template>

<script>
import Context from '@/mixins/Context'
import Iframe from '@/mixins/Iframe'
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'Footer',
  mixins: [Context, Iframe],
  methods: {
    go(path) {
      this.$router.push({path}, this.$_.noop)
    },
    logOut() {
      getCasLogoutUrl().then(() => window.location.href = '/')
    }
  }
}
</script>
