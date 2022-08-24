<template>
  <div id="impact-studio">
    <div v-if="!isLoading && user">
      <SyncDisabled v-if="$currentUser.isAdmin || $currentUser.isTeaching" />
      <div class="d-flex w-100 mb-4">
        <div id="profile-image" class="pr-4">
          <img v-if="user.canvasImage" class="profile-avatar" :src="user.canvasImage" />
        </div>
        <div id="about-user" class="profile-summary-column-variable">
          <h1 id="profile-header-name" class="profile-header-name mb-4">{{ user.canvasFullName }}</h1>
          <div id="profile-looking-for-collaborators">
            {{ user.lookingForCollaborators ? 'Looking for collaborators' : 'Not looking for collaborators' }}
          </div>
          <div id="canvas-course-sections">
            {{ user.canvasCourseSections.join(', ') }}
          </div>
          <div id="profile-last-activity" class="mb-4">
            Last activity:
            <span v-if="user.lastActivity">{{ user.lastActivity | moment('lll') }}</span>
            <span v-if="!user.lastActivity">Never</span>
          </div>
          <div id="profile-personal-description">
            {{ user.personalDescription }}
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
import {getUsers} from '@/api/users'
import Context from '@/mixins/Context'
import SyncDisabled from '@/components/util/SyncDisabled'
import Utils from '@/mixins/Utils'

export default {
  name: 'ImpactStudio',
  mixins: [Context, Utils],
  components: {SyncDisabled},
  data: () => ({
    user: undefined,
    users: []
  }),
  created() {
    this.$loading()
    getUsers().then(data => {
      this.users = data
      const userId = parseInt(this.$route.params.id || this.$currentUser.id)
      this.user = this.$_.find(this.users, {'id': userId})
      console.log(this.user)
      this.$ready()
    })
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
