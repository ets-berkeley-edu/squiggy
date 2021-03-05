<template>
  <div class="align-center d-flex flex-column">
    <h1>Squiggy says HELLO</h1>
    <div class="align-center d-flex flex-column justify-space-between mb-4">
      <v-slider
        v-model="width"
        class="align-self-stretch"
        min="200"
        max="500"
        step="1"
      />
      <v-img
        :aspect-ratio="16 / 9"
        :width="width"
        src="@/assets/hello.jpg"
      />
    </div>

    <ErrorsAlert v-if="errors.length" id="dev-auth-error" :errors="errors" />

    <div v-if="!$currentUser.isAuthenticated">
      <v-card color="transparent" flat>
        <v-form @submit.prevent="devAuth">
          <v-text-field
            id="canvas-api-domain-input"
            v-model="canvasApiDomain"
            outlined
            placeholder="Canvas domain"
            :rules="[rule.notBlank]"
            @input="errors = []"
          />
          <v-text-field
            id="course-site-id-input"
            v-model="canvasCourseId"
            outlined
            placeholder="Canvas course ID"
            :rules="[rule.notBlank, rule.isNumber]"
            @input="errors = []"
          />
          <v-text-field
            id="uid-input"
            v-model="uid"
            outlined
            placeholder="UID"
            :rules="[rule.notBlank, rule.isNumber]"
            @input="errors = []"
          />
          <v-text-field
            id="password-input"
            v-model="password"
            outlined
            placeholder="Password"
            :rules="[rule.notBlank]"
            type="password"
            @input="errors = []"
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
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import ErrorsAlert from '@/components/util/ErrorsAlert'
import Utils from '@/mixins/Utils'
import {devAuthLogIn} from '@/api/auth'

export default {
  name: 'Squiggy',
  components: {ErrorsAlert},
  mixins: [Context, Utils],
  data: () => ({
    canvasApiDomain: undefined,
    canvasCourseId: undefined,
    errors: [],
    idRules: [v => /^\s*\d+\s*$/.test(v) || 'Number required'],
    password: undefined,
    uid: undefined,
    width: 300
  }),
  created() {
    this.$ready()
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
