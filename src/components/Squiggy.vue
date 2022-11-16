<template>
  <div v-if="!isLoading" class="align-center d-flex flex-column my-10">
    <h1 class="grey--text text--darken-2">
      <span v-if="showLennyAndSquiggy">Squiggy</span>
      <span v-if="!showLennyAndSquiggy">SuiteC</span>
      v{{ $config.app.version }}
    </h1>
    <div v-if="$config.app.build">
      <a
        id="link-to-github-commit"
        :href="`https://github.com/ets-berkeley-edu/squiggy/commit/${$config.app.build.gitCommit}`"
        target="_blank"
        aria-label="Open Github in new window"
      >
        <span class="git-commit pr-1">{{ $config.app.build.gitCommit }}</span>
        <i class="fa-brands fa-github" />
      </a>
    </div>
    <div v-if="showLennyAndSquiggy" class="align-center d-flex flex-column justify-space-between mb-4">
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
    <div class="grey--text pb-3 subtitle-1 text--darken-1">
      Hello {{ $currentUser.canvasFullName }}.
    </div>
    <v-expansion-panels v-if="$currentUser.isAuthenticated" class="w-50">
      <v-expansion-panel>
        <v-expansion-panel-header>
          <h2 class="red--text text-no-wrap">
            <div class="align-center d-flex">
              <div class="pr-2">
                <Avatar :user="$currentUser" />
              </div>
              <div>
                User {{ $currentUser.id }}
              </div>
            </div>
          </h2>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <UserSummary :user="$currentUser" />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>
          <h2 class="primary--text text-no-wrap">Course {{ $currentUser.courseId }}</h2>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <CourseSummary :course-id="$currentUser.courseId" />
        </v-expansion-panel-content>
      </v-expansion-panel>
      <v-expansion-panel>
        <v-expansion-panel-header>
          <h2 class="orange--text text-no-wrap">Configs</h2>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <Configs />
        </v-expansion-panel-content>
      </v-expansion-panel>
    </v-expansion-panels>
    <div v-if="$config.developerAuthEnabled && !$currentUser.isAuthenticated">
      <DevAuth />
    </div>
  </div>
</template>

<script>
import Avatar from '@/components/user/Avatar'
import Configs from '@/components/util/Configs'
import CourseSummary from '@/components/course/CourseSummary'
import Context from '@/mixins/Context'
import DevAuth from '@/components/util/DevAuth'
import UserSummary from '@/components/user/UserSummary'
import Utils from '@/mixins/Utils'

export default {
  name: 'Squiggy',
  components: {Avatar, Configs, CourseSummary, DevAuth, UserSummary},
  mixins: [Context, Utils],
  data: () => ({
    showLennyAndSquiggy: undefined,
    width: 300
  }),
  created() {
    this.showLennyAndSquiggy = this.$config.developerAuthEnabled && (this.$config.isVueAppDebugMode || this.$currentUser.isAdmin)
    if (!this.$config.developerAuthEnabled) {
      this.$router.push('/error?m=Sorry, something went wrong. Please contact us if problems persist.')
    }
  }
}
</script>

<style scoped>
.git-commit {
  color: #749461;
  font-size: 18px;
}
</style>
