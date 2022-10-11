<template>
  <v-list dense>
    <v-list-item>
      <v-list-item-content>Canvas User ID</v-list-item-content>
      <v-list-item-content class="align-end">{{ user.canvasUserId }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Name</v-list-item-content>
      <v-list-item-content class="align-end">{{ user.canvasFullName }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Email</v-list-item-content>
      <v-list-item-content class="align-end">{{ user.canvasEmail }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Canvas Course Sections</v-list-item-content>
      <v-list-item-content class="align-end">{{ oxfordJoin(user.canvasCourseSections) }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Canvas Course Groups</v-list-item-content>
      <v-list-item-content class="align-end">{{ oxfordJoin(canvasGroups) }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Canvas Course Role</v-list-item-content>
      <v-list-item-content class="align-end">{{ user.canvasCourseRole }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Admin?</v-list-item-content>
      <v-list-item-content class="align-end">{{ displayBoolean(user.isAdmin) }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Teaching?</v-list-item-content>
      <v-list-item-content class="align-end">{{ displayBoolean(user.isTeaching) }}</v-list-item-content>
    </v-list-item>
    <v-list-item>
      <v-list-item-content>Created At</v-list-item-content>
      <v-list-item-content class="align-end">{{ user.createdAt | moment('lll') }}</v-list-item-content>
    </v-list-item>
  </v-list>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'UserSummary',
  mixins: [Utils],
  props: {
    user: {
      required: true,
      type: Object
    }
  },
  data: () => ({
    canvasGroups: undefined
  }),
  created () {
    this.canvasGroups = this.$_.map(this.user.canvasGroups, canvasGroup => {
      return `${canvasGroup.categoryName} - ${canvasGroup.canvasGroupName}`
    })
  },
  methods: {
    displayBoolean(b) {
      return this.$_.isNil(b) ? '&mdash;' : (b ? 'Yes' : 'No')
    }
  }
}
</script>
