<template>
  <div v-if="!isLoading" class="align-center d-flex flex-column my-10">
    <h1 class="grey--text text--darken-2">Squiggy v{{ $config.squiggyVersion }}</h1>
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
          <h2 class="primary--text text-no-wrap">Canvas Course {{ $currentUser.course.canvasCourseId }}</h2>
        </v-expansion-panel-header>
        <v-expansion-panel-content>
          <CourseSummary :course="$currentUser.course" />
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
    <div v-if="!$currentUser.isAuthenticated">
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
    width: 300
  })
}
</script>
