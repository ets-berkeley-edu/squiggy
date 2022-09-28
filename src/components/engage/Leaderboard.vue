<template>
  <div
    id="leaderboard"
    class="leaderboard"
    :class="$vuetify.theme.dark ? 'dark' : 'light'"
  >
    <v-data-table
      :headers="headers"
      :items="rows"
      disable-pagination
      :hide-default-footer="true"
      :search="search"
    >
      <template #top>
        <div class="d-flex justify-space-between pa-2">
          <div class="d-flex">
            <v-btn
              id="points-configuration-btn"
              class="mr-2"
              @click="go('/engage/points')"
              @keypress.enter="go('/engage/points')"
            >
              Points configuration
            </v-btn>
            <v-btn
              v-if="$currentUser.isAdmin || $currentUser.isTeaching"
              id="download-csv-btn"
              @click="downloadCSV"
              @keypress.enter.prevent="downloadCSV"
            >
              Download CSV
            </v-btn>
          </div>
          <v-text-field
            v-model="search"
            label="Search"
            class="leaderboard-search mb-1"
            hide-details
          />
        </div>
      </template>
      <template v-if="$currentUser.course.protectsAssetsPerSection && ($currentUser.isAdmin || $currentUser.isTeaching)" #header.canvasCourseSections>
        <div class="float-left">
          Course Sections
        </div>
      </template>
      <template #header.canvasFullName>
        <div class="float-left">
          Name
        </div>
      </template>
      <template #header.lastActivity>
        <div class="float-left">
          Last Activity
        </div>
      </template>
      <template #item.canvasCourseSections="{ item }">
        <template v-for="(section, index) in item.canvasCourseSections">
          <div :key="index">{{ section }}</div>
        </template>
      </template>
      <template #item.rank="{ item }">
        <div align="center">
          {{ item.rank }}
        </div>
      </template>
      <template #item.canvasFullName="{ item }">
        <div class="leaderboard-name-outer">
          <img class="leaderboard-avatar" :src="item.canvasImage">
          <div class="leaderboard-name">
            <CrossToolUserLink :user="item" />
          </div>
        </div>
      </template>
      <template #item.lastActivity="{ item }">
        {{ item.lastActivity ? new Date(item.lastActivity).toLocaleString() : '' }}
      </template>
      <template #item.lookingForCollaborators="{ item }">
        <div align="center">
          <v-btn
            v-if="item.lookingForCollaborators && item.id !== $currentUser.id"
            color="success"
            @click="startCanvasConversation(item)"
            @keypress.enter.prevent="startCanvasConversation(item)"
          >
            <v-icon>mdi-account-plus</v-icon><span class="sr-only">Start a conversation</span>
          </v-btn>
        </div>
      </template>
      <template #item.points="{ item }">
        <div align="center">
          {{ item.points }}
        </div>
      </template>
      <template #item.sharePoints="{ item }">
        <div align="center">
          {{ item.sharePoints ? 'Yes' : 'No' }}
        </div>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import CanvasConversation from '@/mixins/CanvasConversation'
import CrossToolUserLink from '@/components/util/CrossToolUserLink'
import Utils from '@/mixins/Utils'

export default {
  name: 'Leaderboard',
  components: {CrossToolUserLink},
  mixins: [CanvasConversation, Utils],
  data() {
    return {
      headers: this.getHeaders(),
      search: ''
    }
  },
  props: {
    rows: {
      required: true,
      type: Array
    }
  },
  methods: {
    downloadCSV() {
      window.location.href = `${this.$config.apiBaseUrl}/api/activities/csv`
    },
    getHeaders() {
      const compareSections = (a, b) => {
        const a_ = this.$_.join(this.$_.map(a, this.$_.trim), ',')
        const b_ = this.$_.join(this.$_.map(b, this.$_.trim), ',')
        return a_.localeCompare(b_)
      }
      const headers = [
        {text: 'Rank', 'value': 'rank'},
        {text: 'Name', 'value': 'canvasFullName'},
        {text: 'Share', 'value': 'sharePoints'},
        {text: 'Points', 'value': 'points'},
        {text: 'Last Activity', 'value': 'lastActivity'}
      ]
      if (!this.$currentUser.isAdmin && !this.$currentUser.isTeaching) {
        headers.splice(2, 1)
      }
      if (this.$currentUser.course.impactStudioUrl) {
        headers.splice(2, 0, {text: 'Collaborate', value: 'lookingForCollaborators'})
      }
      if (this.$currentUser.course.protectsAssetsPerSection && (this.$currentUser.isAdmin || this.$currentUser.isTeaching)) {
        headers.splice(0, 0, {text: 'Course Sections', sort: compareSections, 'value': 'canvasCourseSections'})
      }
      return headers
    }
  }
}
</script>

<style>
.leaderboard table {
  border: 1px solid #ccc;
}
.leaderboard.dark table {
  border: 1px solid #444;
}
.leaderboard tbody tr:nth-of-type(even) {
  background-color: rgba(0, 0, 0, .03);
}
.leaderboard thead th {
  background-color: rgba(0, 0, 0, .03);
  border-color: #aaa !important;
  color: #000 !important;
  font-size: 14px !important;
  text-align: center !important;
}
.leaderboard.dark thead th {
  border-color: #444 !important;
  color: #aaa !important;
}
.leaderboard thead th.text-start {
  text-align: center !important;
}
.leaderboard tbody td {
  border-bottom: none !important;
  padding: 8px !important;
}
.leaderboard-avatar {
  background-color: #ffff;
  background-position: center center;
  background-repeat: no-repeat;
  background-size: cover;
  border: 2px solid #FFF;
  border-radius: 500px;
  height: 40px;
  width: 40px;
}
.leaderboard-cap {
  margin: 12px 5px;
}
.leaderboard-name {
  display: flex;
  line-height: 40px;
  margin-left: 15px;
}
.leaderboard-name-outer {
  display: flex;
}
.leaderboard-search {
  flex-grow: 0.3;
  padding-top: 0;
}
</style>
