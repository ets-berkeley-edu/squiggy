<template>
  <v-list v-if="course" dense>
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
    <v-list-item class="px-3 py-2">
      <v-divider />
    </v-list-item>
    <v-list-item>
      <v-list-item-content>
        <h3 class="subtitle-1">{{ course.users.length }} member{{ course.users.length === 1 ? '' : 's' }}</h3>
        <v-simple-table v-if="course.users.length" dense>
          <template #default>
            <thead>
              <tr>
                <th>Id</th>
                <th>Name</th>
                <th>Role</th>
                <th v-if="allowMasquerade">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="user in course.users"
                :key="user.id"
                :class="{'primary white--text': user.id === $currentUser.id}"
              >
                <td>{{ user.id }}</td>
                <td>{{ user.canvasFullName }}<span v-if="user.id === $currentUser.id"> (you)</span></td>
                <td>{{ user.canvasCourseRole }}</td>
                <td v-if="allowMasquerade">
                  <v-btn
                    v-if="user.id !== $currentUser.id"
                    :id="`become-${user.id}`"
                    icon
                    @click="become(user.id)"
                  >
                    <font-awesome-icon icon="sign-out-alt" />
                    <span class="sr-only">Log in as {{ user.canvasFullName }}</span>
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </template>
        </v-simple-table>
        <div v-if="!course.users.length">
          Course has no users.
        </div>
      </v-list-item-content>
    </v-list-item>
  </v-list>
</template>

<script>
import Utils from '@/mixins/Utils'
import {getCourse} from '@/api/courses'
import {masquerade} from '@/api/auth'

export default {
  name: 'CourseSummary',
  mixins: [Utils],
  props: {
    courseId: {
      required: true,
      type: Number
    }
  },
  data: () => ({
    allowMasquerade: undefined,
    course: undefined
  }),
  created() {
    this.allowMasquerade = this.$config.developerAuthEnabled && (this.$currentUser.isAdmin || this.$config.isVueAppDebugMode)
    getCourse(this.courseId).then(course => {
      this.course = course
    })
  },
  methods: {
    become(userId) {
      const onError = data => {
        this.$router.push(`/error?m=${this.getApiErrorMessage(data)}`)
      }
      masquerade(userId).then(
        data => {
          if (data.isAuthenticated) {
            window.location.href = '/squiggy'
          } else {
            onError(data)
          }
        },
        error => onError(error)
      )
    },
    displayBoolean(b) {
      return this.$_.isNil(b) ? '&mdash;' : (b ? 'Yes' : 'No')
    }
  }
}
</script>
