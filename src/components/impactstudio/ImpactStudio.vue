<template>
  <div id="impact-studio">
    <div v-if="!isLoading && user">
      <SyncDisabled v-if="$currentUser.isAdmin || $currentUser.isTeaching" />
      <div class="d-flex w-100 mb-4">
        <div id="profile-image" class="pr-4">
          <img v-if="user.canvasImage" class="profile-avatar" :src="user.canvasImage" />
        </div>
        <div id="about-user" class="w-100">
          <h1 id="profile-header-name" class="profile-header-name mb-4">{{ user.canvasFullName }}</h1>
          <div id="profile-looking-for-collaborators" class="my-4">
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
    </div>
    <div v-if="!isLoading && !user">
      No user.
    </div>
  </div>
</template>

<script>
import {getUsers, updateLookingForCollaborators, updatePersonalDescription} from '@/api/users'
import Context from '@/mixins/Context'
import SyncDisabled from '@/components/util/SyncDisabled'
import Utils from '@/mixins/Utils'

export default {
  name: 'ImpactStudio',
  mixins: [Context, Utils],
  components: {SyncDisabled},
  data: () => ({
    isMyProfile: false,
    isEditingPersonalDescription: false,
    personalDescription: null,
    user: undefined,
    users: []
  }),
  created() {
    this.$loading()
    getUsers().then(data => {
      this.users = data
      const userId = parseInt(this.$route.params.id || this.$currentUser.id)
      if (this.users) {
        this.user = this.$_.find(this.users, {'id': userId}) || this.users[0]
        this.isMyProfile = !!(this.user && this.user.id === this.$currentUser.id)
        if (this.isMyProfile) {
          this.personalDescription = this.user.personalDescription
        }
      }
      this.$ready()
    })
  },
  methods: {
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
.profile-avatar {
  border-radius: 50%;
  text-align: center;
  width: 100px;
}

.profile-header-name {
  font-size: 25px;
}
</style>
