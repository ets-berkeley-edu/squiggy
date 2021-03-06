<template>
  <div v-if="!$currentUser.isAuthenticated">
    <ErrorsAlert
      v-if="errors.length"
      id="dev-auth-error"
      class="mt-2"
      :errors="errors"
    />
    <v-card color="transparent" flat width="360">
      <v-form @submit="devAuth">
        <div v-if="canvasDomains.length === 1" class="pb-3 text-center">
          <h2 class="grey--text text--darken-2">{{ canvasDomains[0].canvasApiDomain }}</h2>
        </div>
        <v-select
          v-if="canvasDomains.length > 1"
          v-model="canvasApiDomain"
          :items="canvasDomains"
          label="Select Canvas domain..."
          item-text="canvasApiDomain"
          item-value="id"
          outlined
        ></v-select>
        <v-text-field
          id="course-site-id-input"
          v-model="canvasCourseId"
          outlined
          placeholder="Canvas course ID"
          :rules="[rule.notBlank, rule.isNumber]"
          @input="errors = []"
          @keydown.enter="devAuth"
        />
        <v-text-field
          id="uid-input"
          v-model="uid"
          outlined
          placeholder="UID"
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
          :disabled="!canvasApiDomain || !canvasCourseId || !uid || !password || !!errors.length"
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
import Context from '@/mixins/Context'
import ErrorsAlert from '@/components/util/ErrorsAlert'
import Utils from '@/mixins/Utils'
import {devAuthLogIn} from '@/api/auth'

export default {
  name: 'DevAuth',
  components: {ErrorsAlert},
  mixins: [Context, Utils],
  props: {
    canvasDomains: {
      required: true,
      type: Array
    }
  },
  data: () => ({
    canvasApiDomain: undefined,
    canvasCourseId: undefined,
    errors: [],
    password: undefined,
    uid: undefined,
    width: 300
  }),
  created() {
    this.canvasApiDomain = this.canvasDomains.length === 1 ? this.canvasDomains[0].canvasApiDomain : undefined
  },
  methods: {
    devAuth() {
      this.errors = []
      this.validate(this.errors, [this.rule.notBlank], this.canvasApiDomain, 'Invalid Canvas domain')
      this.validate(this.errors, [this.rule.notBlank, this.rule.isNumber], this.canvasCourseId, 'Invalid Canvas course ID')
      this.validate(this.errors, [this.rule.notBlank], this.password, 'Password is required')
      this.validate(this.errors, [this.rule.notBlank, this.rule.isNumber], this.uid, 'Invalid UID')
      if (this.errors.length) {
        this.$putFocusNextTick('canvas-api-domain-input')
      } else {
        devAuthLogIn(this.canvasApiDomain, this.canvasCourseId, this.password, this.uid).then(
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

<style scoped>

</style>