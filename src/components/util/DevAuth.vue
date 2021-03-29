<template>
  <div v-if="!$currentUser.isAuthenticated">
    <Alert
      v-if="errors.length"
      id="dev-auth-error"
      class="mt-2"
      :messages="errors"
      type="error"
    />
    <v-card color="transparent" flat width="360">
      <v-form @submit="devAuth">
        <v-text-field
          id="uid-input"
          v-model="userId"
          outlined
          placeholder="User ID"
          :rules="[rule.notBlank, rule.isNumber]"
          @input="errors = []"
          @keydown.enter="devAuth"
        />
        <v-text-field
          id="password-input"
          v-model="password"
          outlined
          placeholder="Password"
          :rules="[rule.notBlank]"
          type="password"
          @input="errors = []"
          @keydown.enter="devAuth"
        />
        <v-btn
          id="btn-dev-auth-login"
          block
          class="white--text"
          color="red"
          :disabled="!userId || !password || !!errors.length"
          large
          @click="devAuth"
        >
          Dev
          <font-awesome-icon class="mx-2" icon="key" />
          Auth
        </v-btn>
      </v-form>
    </v-card>
  </div>
</template>

<script>
import Alert from '@/components/util/Alert'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {devAuthLogIn} from '@/api/auth'

export default {
  name: 'DevAuth',
  components: {Alert},
  mixins: [Context, Utils],
  data: () => ({
    errors: [],
    password: undefined,
    userId: undefined,
    width: 300
  }),
  methods: {
    devAuth() {
      this.errors = []
      this.validate(this.errors, [this.rule.notBlank], this.password, 'Password is required')
      this.validate(this.errors, [this.rule.notBlank, this.rule.isNumber], this.userId, 'Invalid user ID')
      if (this.errors.length) {
        this.$putFocusNextTick('canvas-api-domain-input')
      } else {
        devAuthLogIn(this.password, this.userId).then(
          data => {
            if (data.isAuthenticated) {
              this.$router.push('/assets', this.$_.noop)
              this.$announcer.set('Welcome to SuiteC', 'polite')
            } else {
              this.errors.push(this.getApiErrorMessage(data))
            }
          },
          error => {
            this.errors.push(error)
          }
        )
      }
    }
  }
}
</script>
