<template>
  <div v-if="!$_.isNil(isCourseActive)">
    <v-alert
      v-if="!isCourseActive"
      role="alert"
      outlined
      color="deep-orange darken-4"
      text
      type="info"
      elevation="2"
    >
      <div class="sync-disabled-header">
        SuiteC syncing is disabled for this course.
      </div>
      <p class="sync-disabled-content">
        After a period of inactivity, the SuiteC tools stop synchronizing their data with the Canvas course site that hosts them. While syncing is disabled:
      </p>
      <ul class="sync-disabled-content">
        <li>Changes in course site membership and user roles will not be reflected in the SuiteC tools.</li>
        <li>Assignment submissions will not sync to the Asset Library.</li>
        <li>Assignment submissions and Discussions activity will not be tracked in the Engagement Index.</li>
      </ul>
      <p class="sync-disabled-content">
        If you resume syncing, the SuiteC tools will update to reflect submissions, activities and membership changes that took place while syncing was disabled.
      </p>
      <div class="d-flex justify-center">
        <v-btn
          type="button"
          @click="reactivateCourse"
          @keypress.enter="reactivateCourse"
        >
          <span v-if="!activating">Resume syncing</span>
          <span v-if="activating">Resuming...</span>
        </v-btn>
      </div>
    </v-alert>

    <v-alert
      v-if="reactivated"
      role="alert"
      outlined
      text
      type="success"
      elevation="2"
    >
      Syncing has been resumed for this course. There may be a short delay before SuiteC tools are updated.
    </v-alert>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'
import {activate, isCurrentCourseActive} from '@/api/courses'

export default {
  name: 'SyncDisabled',
  mixins: [Context, Utils],
  data: () => ({
    activating: false,
    isCourseActive: undefined,
    reactivated: false
  }),
  created() {
    isCurrentCourseActive().then(data => {
      this.isCourseActive = data
    })
  },
  methods: {
    reactivateCourse() {
      this.activating = true
      activate().then(data => {
        this.isCourseActive = data
        this.activating = false
        this.reactivated = true
      })
    }
  }
}
</script>

<style scoped>
.sync-disabled-content {
  margin: 15px 0;
}
.sync-disabled-header {
  font-weight: 600;
  margin: 0;
}
</style>
