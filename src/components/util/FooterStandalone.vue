<template>
  <v-footer id="footer" app>
    <v-container fluid class="pa-1">
      <v-row no-gutters justify="space-between">
        <v-col>
          <div class="align-center d-flex">
            <div>
              <v-btn
                id="go-home-btn"
                :disabled="$router.currentRoute.meta.isLoginPage"
                icon
                @click="go('/squiggy')"
              >
                <span class="sr-only">Go home</span>
                <font-awesome-icon icon="home" size="lg" />
              </v-btn>
            </div>
            <div>
              <DarkModeToggle />
            </div>
            <div class="px-2">|</div>
            <div>
              <v-btn id="go-asset-library-btn" icon @click="go('/assets')">
                <span class="sr-only">Go to Asset Library</span>
                <font-awesome-icon icon="images" />
              </v-btn>
            </div>
            <div>
              <v-btn id="go-engagement-index-btn" icon @click="go('/engage')">
                <span class="sr-only">Go to Engagement Index</span>
                <font-awesome-icon icon="list-ol" />
              </v-btn>
            </div>
            <div v-if="$config.featureFlagWhiteboards">
              <v-btn id="go-whiteboards-btn" icon @click="go('/whiteboards')">
                <span class="sr-only">Go to Whiteboards</span>
                <font-awesome-icon icon="palette" />
              </v-btn>
            </div>
          </div>
        </v-col>
        <v-col>
          <div class="float-right">
            <div class="align-center d-flex">
              <div>
                {{ $_.get($announcer, 'data.content') }}
              </div>
              <div v-if="$_.get($announcer, 'data.content')" class="pl-2">
                |
              </div>
              <div>
                <v-btn id="log-out-btn" icon @click="logOut">
                  <span class="sr-only">Log Out</span>
                  <font-awesome-icon icon="sign-out-alt" size="lg" />
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
import DarkModeToggle from '@/components/util/DarkModeToggle'
import Utils from '@/mixins/Utils'
import {getCasLogoutUrl} from '@/api/auth'

export default {
  name: 'FooterStandalone',
  mixins: [Context, Utils],
  components: {DarkModeToggle},
  methods: {
    logOut() {
      this.$announcer.polite('Logging out')
      getCasLogoutUrl().then(() => window.location.href = '/squiggy')
    }
  }
}
</script>
