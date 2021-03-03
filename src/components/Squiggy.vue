<template>
  <div class="text-center">
    <h1>Squiggy says HELLO</h1>
    <div class="d-flex flex-column justify-space-between align-center">
      <v-slider
        v-model="width"
        class="align-self-stretch"
        min="200"
        max="500"
        step="1"
      ></v-slider>
      <v-img
        :aspect-ratio="16/9"
        :width="width"
        src="@/assets/hello.jpg"
      ></v-img>
    </div>
    <v-card class="opaque-card pa-4" color="transparent" flat>
      <v-form @submit.prevent="devAuth">
        <v-text-field
          id="dev-auth-uid"
          v-model="devAuthUid"
          background-color="white"
          outlined
          placeholder="UID"
          :rules="[v => !!v || 'Required']"
        ></v-text-field>
        <v-text-field
          id="dev-auth-password"
          v-model="devAuthPassword"
          background-color="white"
          outlined
          placeholder="Password"
          :rules="[v => !!v || 'Required']"
          type="password"
        ></v-text-field>
        <v-btn
          id="btn-dev-auth-login"
          block
          :color="!devAuthUid || !devAuthPassword ? 'red lighten-2' : 'red'"
          dark
          large
          @click="devAuth"
        >
          Dev
          <v-icon dark>mdi-emoticon-devil-outline</v-icon>
          Auth
        </v-btn>
      </v-form>
    </v-card>
  </div>
</template>

<script>
import {devAuthLogIn} from '@/api/auth'

export default {
  name: 'Squiggy',
  data: () => ({
    devAuthUid: undefined,
    devAuthPassword: undefined,
    width: 300,
  }),
  created() {
    this.$ready()
  },
  methods: {
    devAuth() {
      let uid = this.$_.trim(this.devAuthUid)
      let password = this.$_.trim(this.devAuthPassword)
      if (uid && password) {
        devAuthLogIn(uid, password).then(data => {
            if (data.isAuthenticated) {
              this.$router.push('/assets', this.$_.noop)
              this.alertScreenReader('Welcome to SuiteC')
            } else {
              const message = this.$_.get(data, 'response.data.message') || this.$_.get(data, 'message') || 'Authentication failed'
              // TODO: Show error in UI
              console.log(message)
            }
          },
           error => {
             console.log(error)
           }
        )
      } else if (uid) {
        console.log('Password required')
        this.$putFocusNextTick('dev-auth-password')
      } else {
        console.log('Both UID and password are required')
        this.$putFocusNextTick('dev-auth-uid')
      }
    }
  }
}
</script>
