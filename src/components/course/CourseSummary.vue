<template>
  <v-list dense>
    <v-list-item>
      <v-list-item-content>Active</v-list-item-content>
      <v-list-item-content class="align-end">{{ displayBoolean(course.active) }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Canvas Course Site</v-list-item-content>
      <v-list-item-content class="align-end">
        <a
          :id="`canvas-course-site-${course.canvasCourseId}`"
          aria-label="Open Canvas course site in a new window"
          :href="`${$config.canvasBaseUrl}/courses/${course.canvasCourseId}`"
          target="_blank"
        >
          Canvas Course <span id="canvas-course-site-id">{{ course.canvasCourseId }}</span>
        </a>
      </v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Notifications, Daily?</v-list-item-content>
      <v-list-item-content class="align-end">{{ displayBoolean(course.enableDailyNotifications) }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Notifications, Weekly?</v-list-item-content>
      <v-list-item-content class="align-end">{{ displayBoolean(course.enableWeeklyNotifications) }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Upload enable?</v-list-item-content>
      <v-list-item-content class="align-end">{{ displayBoolean(course.enableUpload) }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>URL, Asset Library</v-list-item-content>
      <v-list-item-content class="align-end">{{ course.assetLibraryUrl || '&mdash;' }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>URL, Engagement Index</v-list-item-content>
      <v-list-item-content class="align-end">{{ course.engagementIndexUrl || '&mdash;' }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Created At</v-list-item-content>
      <v-list-item-content class="align-end">{{ course.createdAt | moment('lll') }}</v-list-item-content>
    </v-list-item>
  </v-list>
</template>

<script>
export default {
  name: 'CourseSummary',
  props: {
    course: {
      required: true,
      type: Object
    }
  },
  methods: {
    displayBoolean(b) {
      return this.$_.isNil(b) ? '&mdash;' : (b ? 'Yes' : 'No')
    }
  }
}
</script>
