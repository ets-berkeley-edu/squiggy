<template>
  <div id="impact-studio">
    <div v-if="!isLoading && user">
      <SyncDisabled v-if="$currentUser.isAdmin || $currentUser.isTeaching" />
      <div class="d-flex align-baseline">
        <div>Find user:</div>
        <div class="w-25 mx-3">
          <select id="find-user-select" v-model="findUserId" class="native-select">
            <option v-for="u in users" :key="u.id" :value="u.id">
              {{ u.canvasFullName }}
            </option>
          </select>
        </div>
        <v-btn
          id="find-user-apply"
          color="primary"
          @click="goToProfile(findUserId)"
          @keypress.enter.prevent="goToProfile(findUserId)"
        >
          Go
        </v-btn>
      </div>
      <div class="d-flex justify-space-between w-100 mb-4">
        <div id="previous-user">
          <a v-if="previousUser" :href="`/impact_studio/profile/${previousUser.id}`">
            &lt; {{ previousUser.canvasFullName }}
          </a>
        </div>
        <div id="next-user">
          <a v-if="nextUser" :href="`/impact_studio/profile/${nextUser.id}`">
            {{ nextUser.canvasFullName }} &gt;
          </a>
        </div>
      </div>
      <div class="d-flex w-100 mb-4">
        <div id="profile-image" class="pr-4">
          <img v-if="user.canvasImage" class="profile-avatar" :src="user.canvasImage" />
        </div>
        <div id="about-user" class="w-100">
          <h1 id="profile-header-name" class="profile-header-name mb-4">{{ user.canvasFullName }}</h1>
          <div v-if="isMyProfile" id="profile-looking-for-collaborators" class="my-4">
            {{ user.lookingForCollaborators ? 'Looking for collaborators' : 'Not looking for collaborators' }}
            <v-btn
              id="toggle-looking-for-collaborators-btn"
              class="mx-2"
              @click="toggleLookingForCollaborators"
              @keypress.enter="toggleLookingForCollaborators"
            >
              Change
            </v-btn>
          </div>
          <div v-if="!isMyProfile & user.lookingForCollaborators" id="profile-looking-for-collaborators" class="my-4">
            <v-btn
              id="toggle-looking-for-collaborators-btn"
              color="success"
              @click="startCanvasConversation(user)"
              @keypress.enter.prevent="startCanvasConversation(user)"
            >
              <v-icon class="pr-2">mdi-account-plus</v-icon>
              Looking for Collaborators
            </v-btn>
          </div>
          <div v-if="user.canvasCourseSections" id="canvas-course-sections">
            {{ user.canvasCourseSections.join(', ') }}
          </div>
          <div id="profile-last-activity">
            Last activity:
            <span v-if="user.lastActivity">{{ user.lastActivity | moment('from', 'now') }}</span>
            <span v-if="!user.lastActivity">Never</span>
          </div>
          <div v-if="!isEditingPersonalDescription" id="profile-personal-description" class="my-4">
            <div
              v-linkified:options="linkifyOptions"
              class="my-4 pt-1 pb-2"
              v-html="user.personalDescription"
            />
            <div class="pt-3">
              <v-btn
                v-if="isMyProfile"
                id="profile-personal-description-edit-btn"
                @click="isEditingPersonalDescription = true"
                @keypress.enter="isEditingPersonalDescription = true"
              >
                Edit
              </v-btn>
            </div>
          </div>
          <div v-if="isEditingPersonalDescription" id="profile-personal-description-edit" class="my-4">
            <v-text-field
              id="profile-personal-description-input"
              v-model="personalDescription"
              class="mt-4"
              counter
              label="Short Personal Description or Collaboration Interests"
              maxlength="255"
              :rules="[v => (!v || v.length <= 255) || 'Personal Description must be 255 characters or less']"
              solo
              @keydown.enter.prevent
            />
            <div class="d-flex">
              <v-btn
                id="confirm-personal-description-btn"
                class="mr-2"
                color="primary"
                @click="personalDescriptionSave"
                @keypress.enter="personalDescriptionSave"
              >
                Save
              </v-btn>
              <v-btn
                id="cancel-personal-description-btn"
                class="mr-2"
                @click="personalDescriptionCancel"
                @keypress.enter="personalDescriptionCancel"
              >
                Cancel
              </v-btn>
            </div>
          </div>
        </div>
      </div>
      <div v-if="courseInteractions" id="activity-network" class="my-4 w-100">
        <div class="mb-3">
          <h2 class="impact-studio-section-header">Activity Network</h2>
          <div>
            See how you and others are connected.
          </div>
        </div>
        <ActivityNetwork
          :course-interactions="courseInteractions"
          :user="user"
          :users="users"
        />
        <div v-if="!courseInteractions.length">
          No activity detected in this course.
        </div>
      </div>
      <div id="activity-timeline" class="my-4 w-100">
        <div class="mb-3">
          <h2 class="impact-studio-section-header">Activity Timeline</h2>
          <div>
            Your individual actions and others' responses to your actions over time.
          </div>
        </div>
        <ActivityTimeline
          v-if="showActivities"
          :activities="userActivities"
        />
      </div>
      <AssetSwimlane
        id-prefix="user-assets"
        :assets="userAssets"
        :fetch-assets="fetchUserAssets"
        :show-more="userAssetsMore"
        :title="isMyProfile ? 'My Assets' : `${user.canvasFullName}'s Assets`"
        :user="user"
        class="my-4"
      />
      <AssetSwimlane
        v-if="isMyProfile"
        id-prefix="everyones-assets"
        :assets="everyonesAssets"
        :fetch-assets="fetchEveryonesAssets"
        :show-more="everyonesAssetsMore"
        title="Everyone's Assets"
        class="my-4"
      />
    </div>
    <div v-if="!isLoading && !user">
      No user.
    </div>
  </div>
</template>

<script>
import {getAssets} from '@/api/assets'
import {getCourseInteractions, getUserActivities} from '@/api/activities'
import {getUsers, updateLookingForCollaborators, updatePersonalDescription} from '@/api/users'
import ActivityNetwork from '@/components/impactstudio/ActivityNetwork'
import ActivityTimeline from '@/components/impactstudio/ActivityTimeline'
import AssetSwimlane from '@/components/impactstudio/AssetSwimlane'
import CanvasConversation from '@/mixins/CanvasConversation'
import Context from '@/mixins/Context'
import SyncDisabled from '@/components/util/SyncDisabled'
import Utils from '@/mixins/Utils'

export default {
  name: 'ImpactStudio',
  mixins: [CanvasConversation, Context, Utils],
  components: {ActivityNetwork, ActivityTimeline, AssetSwimlane, SyncDisabled},
  data: () => ({
    courseInteractions: null,
    everyonesAssets: [],
    everyonesAssetsMore: false,
    findUserId: null,
    isMyProfile: false,
    isEditingPersonalDescription: false,
    linkifyOptions: {},
    nextUser: null,
    personalDescription: null,
    previousUser: null,
    showActivities: false,
    user: undefined,
    userActivities: {},
    userAssets: [],
    userAssetsMore: false,
    users: []
  }),
  created() {
    this.$loading()
    const baseUrl = this.$config.baseUrl
    this.linkifyOptions = {
      formatHref: {
        hashtag: href => `${baseUrl}/assets#suitec_keywords=${href.substring(1)}`
      }
    }
    getUsers().then(data => {
      this.users = data
      const userId = parseInt(this.$route.params.id || this.$currentUser.id)
      if (this.users) {
        const userIndex = this.$_.findIndex(this.users, {'id': userId}) || 0
        this.user = this.users[userIndex]
        this.nextUser = this.users[(userIndex + 1) % this.users.length]
        this.previousUser = this.users[(userIndex || this.users.length) - 1]
        this.isMyProfile = !!(this.user && this.user.id === this.$currentUser.id)
        if (this.isMyProfile) {
          this.personalDescription = this.user.personalDescription
        }
        if (this.user) {
          getUserActivities(this.user.id).then(data => {
            this.userActivities = data
            this.showActivities = true
          })
        }
        getCourseInteractions().then(data => {
          this.courseInteractions = data
        })
      }
      this.$ready()
    })
  },
  methods: {
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true})),
    fetchEveryonesAssets(orderBy) {
      this.everyonesAssets = this.getSkeletons(4)
      return getAssets({offset: 0, limit: 4, orderBy: orderBy}).then((data) => {
        this.everyonesAssets = data.results || []
        this.everyonesAssetsMore = !!data.total && data.total > 4
      })
    },
    fetchUserAssets(orderBy) {
      this.userAssets = this.getSkeletons(4)
      return getAssets({offset: 0, limit: 4, orderBy: orderBy, userId: this.user.id}).then((data) => {
        this.userAssets = data.results || []
        this.userAssetsMore = !!data.total && data.total > 4
      })
    },
    goToProfile(userId) {
      this.$router.push({path: `/impact_studio/profile/${userId}`})
    },
    personalDescriptionCancel() {
      this.$announcer.polite('Canceled')
      this.personalDescription = this.user.personalDescription
      this.isEditingPersonalDescription = false
    },
    personalDescriptionSave() {
      updatePersonalDescription(this.personalDescription).then((data) => {
        this.$announcer.polite('Saved')
        this.user.personalDescription = data.personalDescription
        this.personalDescription = this.user.personalDescription
        this.isEditingPersonalDescription = false
      })
    },
    toggleLookingForCollaborators() {
      updateLookingForCollaborators(!this.user.lookingForCollaborators).then((data) => {
        this.$announcer.polite('Looking for collaborators turned ' + (data.lookingForCollaborators ? 'on' : 'off'))
        this.user.lookingForCollaborators = data.lookingForCollaborators
      })
    }
  }
}
</script>

<style>
.impact-studio-section-header {
  font-size: 22px;
}
</style>

<style scoped>
.profile-avatar {
  border-radius: 50%;
  text-align: center;
  width: 100px;
}

.profile-header-name {
  font-size: 25px;
}
</style>
