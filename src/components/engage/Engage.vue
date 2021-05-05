<template>
  <div id="engagement-index">
    <div class="mb-2 mt-2">
      <h2>Engagement Index</h2>
    </div>
    <div v-if="!$currentUser.isAdmin && !$currentUser.isTeaching && ($currentUser.sharePoints === null)" id="engagement-splash" class="float-none">
      The engagement index is a scoreboard that lists the names and scores of all the students taking this course. If you do not wish to share your engagement score, uncheck the box below and click 'Continue'.
    </div>
    <div
      v-if="!$currentUser.isAdmin && !$currentUser.isTeaching && ($currentUser.sharePoints !== null)"
      id="engagement-userinfo"
      class="engagement-userinfo-container"
    >
      <div v-if="showLeaderboard" class="engagement-userinfo-badge">
        <div class="engagement-userinfo-badge-title">My Rank</div>
        <div id="engagement-userinfo-points" class="engagement-userinfo-badge-data">{{ rank }}</div>
      </div>
      <div class="engagement-userinfo-badge">
        <div class="engagement-userinfo-badge-title">My Points</div>
        <div id="engagement-userinfo-points" class="engagement-userinfo-badge-data">{{ $currentUser.points }}</div>
      </div>
      <div v-if="showLeaderboard" class="engagement-userinfo-badge engagement-userinfo-boxplot-container">
        <div class="engagement-userinfo-badge-title">How do I compare</div>
        <div id="engagement-userinfo-boxplot" class="engagement-userinfo-boxplot" />
      </div>
    </div>

    <div v-if="showLeaderboard" class="engagement-container">
      <Leaderboard />
    </div>

    <div class="engagement-container">
      <h3>Share my score</h3>
      <v-form class="engagement-share-form" @submit="saveSharePoints">
        <v-checkbox
          id="share-my-score"
          v-model="sharePoints"
          @change="toggleSharePoints"
        />
        <label for="share-my-score">
          Yes, I want to share my score on the Engagement Index
        </label>
        <v-btn v-if="!$currentUser.isAdmin && !$currentUser.isTeaching && $currentUser.sharePoints === null" type="submit">Continue</v-btn>
      </v-form>
    </div>
  </div>
</template>

<script>
import Leaderboard from '@/components/engage/Leaderboard'
import {getLeaderboard, updateSharePoints} from '@/api/users'

export default {
  name: 'Engage',
  components: {Leaderboard},
  data() {
    return {
      rank: 666,
      sharePoints: this.setInitialSharePoints(),
      showLeaderboard: false
    }
  },
  created() {
    this.refreshLeaderboard()
  },
  methods: {
    refreshLeaderboard() {
      if (this.$currentUser.isAdmin || this.$currentUser.isTeaching || this.$currentUser.sharePoints) {
        this.$loading()
        getLeaderboard().then(() => {
          this.showLeaderboard = true
          this.$ready('Engagement Index')
        })
      } else {
        this.showLeaderboard = false
      }
    },
    saveSharePoints() {
      updateSharePoints(this.sharePoints).then((data) => {
        this.$currentUser.sharePoints = data.sharePoints
        this.$announcer.polite(this.sharePoints ? 'Sharing points' : 'Not sharing points')
        this.refreshLeaderboard()
      })
    },
    setInitialSharePoints() {
      if (!this.$currentUser.isAdmin && !this.$currentUser.isTeaching && this.$currentUser.sharePoints === null) {
        return true
      } else {
        return this.$currentUser.sharePoints
      }
    },
    toggleSharePoints() {
      if (this.$currentUser.isAdmin || this.$currentUser.isTeaching || this.$currentUser.sharePoints !== null) {
        this.saveSharePoints()
      }
    }
  }
}
</script>

<style scoped>
.engagement-container {
  clear: both;
  margin-top: 20px;
}

.engagement-container label {
  font-weight: 300;
  margin: 0 20px 0 0;
}

.engagement-share-form {
  align-items: center;
  display: flex;
}

.engagement-userinfo-badge {
  background-color: #eee;
  border-radius: 4px;
  color: #444;
  float: left;
  margin-bottom: 20px;
  margin-right: 25px;
  padding: 10px;
  text-align: center;
  width: 150px;
}

.engagement-userinfo-badge-data {
  font-size: 48px;
  font-weight: 300;
  line-height: 60px;
}

.engagement-userinfo-badge-title {
  font-size: 14px;
  padding: 2px;
  text-transform: uppercase;
}

.engagement-userinfo-boxplot-container {
  width: 300px;
}

.engagement-userinfo-boxplot {
  height: 60px;
  width: 290px;
}

.engagement-userinfo-boxplot .highcharts-container, svg {
  overflow: visible !important;
}

.engagement-userinfo-boxplot-container .highcharts-tooltip {
  background-color: #000;
  border-color: #000;
  border-radius: 6px;
  padding: 8px;
}

.engagement-userinfo-boxplot-container g.highcharts-tooltip {
  display: none !important;
}

.engagement-userinfo-boxplot-container .highcharts-tooltip span {
  left: 0 !important;
  position: relative !important;
  top: 0 !important;
}

.engagement-userinfo-container {
  clear: both;
  margin-bottom: 10px;
}
</style>
