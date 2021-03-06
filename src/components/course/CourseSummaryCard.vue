<template>
  <v-card
    class="mx-auto"
    max-width="500"
  >
    <v-card-text>
      <div class="display-1 text--primary text-no-wrap">
        Canvas Course {{ course.canvasCourseId }}
      </div>
      <div class="text--primary">
        <v-list dense>
          <v-list-item>
            <v-list-item-content>Active</v-list-item-content>
            <v-list-item-content class="align-end"></v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>Notifications, Daily?</v-list-item-content>
            <v-list-item-content class="align-end">{{ course.enableDailyNotifications ? 'Yes' : 'No' }}</v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>Notifications, Weekly?</v-list-item-content>
            <v-list-item-content class="align-end">{{ course.enableWeeklyNotifications ? 'Yes' : 'No' }}</v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>Upload enable?</v-list-item-content>
            <v-list-item-content class="align-end">{{ course.enableUpload ? 'Yes' : 'No' }}</v-list-item-content>
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
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'CourseSummaryCard',
  props: {
    course: {
      required: true,
      type: Object
    }
  }
}
</script>
