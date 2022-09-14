<template>
  <div id="impact-studio">
    <div v-if="!isLoading && user">
      <SyncDisabled v-if="$currentUser.isAdmin || $currentUser.isTeaching" />
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
          <div id="profile-looking-for-collaborators" class="my-4">
            {{ user.lookingForCollaborators ? 'Looking for collaborators' : 'Not looking for collaborators' }}
            <v-btn
              v-if="isMyProfile"
              id="toggle-looking-for-collaborators-btn"
              class="mx-2"
              @click="toggleLookingForCollaborators"
              @keypress.enter="toggleLookingForCollaborators"
            >
              Change
            </v-btn>
          </div>
          <div v-if="user.canvasCourseSections" id="canvas-course-sections">
            {{ user.canvasCourseSections.join(', ') }}
          </div>
          <div id="profile-last-activity">
            Last activity:
            <span v-if="user.lastActivity">{{ user.lastActivity | moment('lll') }}</span>
            <span v-if="!user.lastActivity">Never</span>
          </div>
          <div v-if="!isEditingPersonalDescription" id="profile-personal-description" class="my-4">
            <div>
              {{ user.personalDescription }}
            </div>
            <div>
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
          <div v-if="isEditingPersonalDescription" id="profile-personal-description-edit">
            <v-text-field
              id="profile-personal-description-input"
              v-model="personalDescription"
              label="Short Personal Description or Collaboration Interests"
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
        <div v-for="(interaction, index) in courseInteractions" :key="index">
          {{ courseInteractions }}
        </div>
        <div v-if="!courseInteractions.length">
          No activity detected in this course.
        </div>
      </div>
      <div v-if="userActivities" id="activity-timeline" class="my-4 w-100">
        <div class="mb-3">
          <h2 class="impact-studio-section-header">Activity Timeline</h2>
          <div>
            Your individual actions and others' responses to your actions over time.
          </div>
        </div>
        <div id="activity-timeline-contributions" class="mb-3">
          <h3>Contributions (activities you do)</h3>
          <div>
            <h4>Views/Likes</h4>
            <div>
              {{ userActivities.actions.engagements }}
            </div>
            <h4>Interactions</h4>
            <div>
              {{ userActivities.actions.interactions }}
            </div>
            <h4>Creations</h4>
            <div>
              {{ userActivities.actions.creations }}
            </div>
          </div>
        </div>
        <div id="activity-timeline-impacts" class="mb-3">
          <h3>Impacts (others responding to your activities)</h3>
          <div>
            <h4>Views/Likes</h4>
            <div>
              {{ userActivities.impacts.engagements }}
            </div>
            <h4>Interactions</h4>
            <div>
              {{ userActivities.impacts.interactions }}
            </div>
            <h4>Reuses</h4>
            <div>
              {{ userActivities.impacts.creations }}
            </div>
          </div>
        </div>
        <div id="user-assets">
          <h2 class="impact-studio-section-header">
            {{ isMyProfile ? 'My Assets' : `${user.canvasFullName}'s Assets` }}
          </h2>
          <v-card
            v-if="userAssetsLane.length"
            class="d-flex flex-wrap"
            flat
            tile
          >
            <AssetCard
              v-for="(asset, index) in userAssetsLane"
              :key="index"
              :asset="asset"
              class="asset-card ma-3"
            />
          </v-card>
          <div v-if="!userAssetsLane.length">
            No assets.
          </div>
        </div>
        <div v-if="isMyProfile" id="everyones-assets">
          <h2 class="impact-studio-section-header">Everyone's Assets</h2>
          <v-card
            v-if="everyonesAssetsLane.length"
            class="d-flex flex-wrap"
            flat
            tile
          >
            <AssetCard
              v-for="(asset, index) in everyonesAssetsLane"
              :key="index"
              :asset="asset"
              class="asset-card ma-3"
            />
          </v-card>
          <div v-if="!everyonesAssetsLane.length">
            No assets.
          </div>
        </div>
      </div>
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
import AssetCard from '@/components/assets/AssetCard'
import Context from '@/mixins/Context'
import SyncDisabled from '@/components/util/SyncDisabled'
import Utils from '@/mixins/Utils'

export default {
  name: 'ImpactStudio',
  mixins: [Context, Utils],
  components: {AssetCard, SyncDisabled},
  data: () => ({
    courseInteractions: null,
    everyonesAssetsLane: [],
    everyonesAssetsOrderBy: 'recent',
    isMyProfile: false,
    isEditingPersonalDescription: false,
    nextUser: null,
    personalDescription: null,
    previousUser: null,
    user: undefined,
    userActivities: null,
    userAssetsLane: [],
    userAssetsOrderBy: 'recent',
    users: []
  }),
  created() {
    this.$loading()
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
          this.fetchEveryonesAssets()
        }
        getUserActivities(this.user.id).then(data => {
          this.userActivities = data
        })
        getCourseInteractions().then(data => {
          this.courseInteractions = data
        })
        this.fetchUserAssets(this.user.id)
      }
      this.$ready()
    })
  },
  methods: {
    getSkeletons: count => Array.from(new Array(count), () => ({isLoading: true})),
    fetchEveryonesAssets() {
      this.everyonesAssetsLane = this.getSkeletons(4)
      getAssets({offset: 0, limit: 4, orderBy: this.everyonesAssetsOrderBy}).then((data) => {
        this.everyonesAssetsLane = data.results || []
      })
    },
    fetchUserAssets(userId) {
      this.userAssetsLane = this.getSkeletons(4)
      getAssets({offset: 0, limit: 4, orderBy: this.userAssetsOrderBy, userId: userId}).then((data) => {
        this.userAssetsLane = data.results || []
      })
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

<style scoped>
.impact-studio-section-header {
  font-size: 22px;
}

.profile-avatar {
  border-radius: 50%;
  text-align: center;
  width: 100px;
}

.profile-header-name {
  font-size: 25px;
}
</style>
