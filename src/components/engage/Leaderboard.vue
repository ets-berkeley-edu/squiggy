<template>
  <div id="leaderboard" class="leaderboard">
    <v-data-table
      :headers="headers"
      :items="rows"
      disable-pagination
      :hide-default-footer="true"
      :search="search"
    >
      <template #top>
        <div class="d-flex justify-space-between">
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
              :href="`${$config.apiBaseUrl}/api/activities/csv`"
            >
              Download CSV
            </v-btn>
          </div>
          <v-text-field
            v-model="search"
            label="Search"
            class="leaderboard-search"
          />
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
      <template #item.rank="{ item }">
        <div align="center">
          {{ item.rank }}
        </div>
      </template>
      <template #item.canvasFullName="{ item }">
        <div class="leaderboard-name-outer">
          <img class="leaderboard-avatar" :src="item.canvasImage">
          <div class="leaderboard-name">
            <UserLink :user="item" :cross-tool-link="true" />
          </div>
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
      <template #item.lastActivity="{ item }">
        {{ item.lastActivity ? new Date(item.lastActivity).toLocaleString() : '' }}
      </template>
    </v-data-table>
  </div>
</template>

<script>
import UserLink from '@/components/util/UserLink'
import Utils from '@/mixins/Utils'

export default {
  name: 'Leaderboard',
  components: {UserLink},
  mixins: [Utils],
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
    getHeaders() {
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
      return headers
    }
  }
}
</script>

<style>
.leaderboard table {
  border: 1px solid #ccc;
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
