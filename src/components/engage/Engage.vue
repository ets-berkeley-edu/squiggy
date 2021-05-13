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
      <div v-if="showLeaderboard && rank" class="engagement-userinfo-badge">
        <div class="engagement-userinfo-badge-title">My Rank</div>
        <div id="engagement-userinfo-rank" class="engagement-userinfo-badge-data">{{ rank }}</div>
      </div>
      <div class="engagement-userinfo-badge">
        <div class="engagement-userinfo-badge-title">My Points</div>
        <div id="engagement-userinfo-points" class="engagement-userinfo-badge-data">{{ $currentUser.points }}</div>
      </div>
      <div v-if="showLeaderboard && boxplotOptions" class="engagement-userinfo-badge engagement-userinfo-boxplot-container">
        <div class="engagement-userinfo-badge-title">How do I compare</div>
        <div id="engagement-userinfo-boxplot" class="engagement-userinfo-boxplot">
          <highcharts :options="boxplotOptions" />
        </div>
      </div>
    </div>

    <div v-if="showLeaderboard" class="engagement-container">
      <Leaderboard :rows="leaderboard" />
    </div>

    <div v-if="!showLeaderboard && $currentUser.sharePoints === false" class="engagement-container">
      <v-btn
        id="points-configuration-btn"
        class="mr-2"
        @click="go('/engage/points')"
        @keypress.enter="go('/engage/points')"
      >
        Points configuration
      </v-btn>
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
import Utils from '@/mixins/Utils'
import {getLeaderboard, updateSharePoints} from '@/api/users'

export default {
  name: 'Engage',
  mixins: [Utils],
  components: {Leaderboard},
  data() {
    return {
      boxplotOptions: null,
      leaderboard: null,
      rank: null,
      sharePoints: this.setInitialSharePoints(),
      showLeaderboard: false
    }
  },
  created() {
    this.refreshLeaderboard()
  },
  methods: {
    calculateBoxPlotData(series) {
      series.sort((a, b) => b - a)
      const min = series[0]
      const max = series[series.length - 1]
      const q1 = this.calculateQuartile(series, 1)
      const q2 = this.calculateQuartile(series, 2)
      const q3 = this.calculateQuartile(series, 3)
      return [
        max,
        q3,
        q2,
        q1,
        min
      ]
    },
    calculateQuartile(series, quartile) {
      const quartileIndex = Math.floor(series.length / 4 * quartile)
      // If the quartile point lands in between 2 items, calculate the average of those items
      if (series.length % 2 === 1 && series[quartileIndex - 1]) {
        return (series[quartileIndex - 1] + series[quartileIndex]) / 2
      // If the quartile point lands on an item in the series, return that value
      } else {
        return series[quartileIndex]
      }
    },
    rankLeaderboard() {
      for (const [index, row] of this.leaderboard.entries()) {
        row.rank = index + 1
        if (row.id === this.$currentUser.id) {
          this.rank = row.rank
        }
      }
    },
    refreshBoxplot() {
      const points = this.leaderboard.map(e => e.points)
      const boxplotData = this.calculateBoxPlotData(points)

      // No boxplot without sufficient unique data points.
      if (this.$_.uniq(boxplotData).length < 2) {
        this.boxplotOptions = null
        return
      }

      this.boxplotOptions = {
        chart: {
          backgroundColor: 'transparent',
          height: 80,
          inverted: true,
          margin: [0, 20, 0, 20],
          type: 'boxplot'
        },
        credits: {
          enabled: false
        },
        legend: {
          enabled: false
        },
        plotOptions: {
          boxplot: {
            color: '#88acc4',
            fillColor: '#88acc4',
            lineWidth: 1,
            medianColor: '#eee',
            medianWidth: 3,
            whiskerLength: 20,
            whiskerWidth: 3
          }
        },
        series: [
          {
            data: [boxplotData],
            pointWidth: 40,
            tooltip: {
              borderColor: 'transparent',
              headerFormat: '',
              pointFormat: 'Maximum: {point.high}<br/>' +
                'Upper Quartile: {point.q3}<br/>' +
                'Median: {point.median}<br/>' +
                'Lower Quartile: {point.q1}<br/>' +
                'Minimum: {point.low}'
            }
          },
          {
            data: [[0, this.$currentUser.points]],
            marker: {
              fillColor: '#3179bc',
              lineWidth: 5,
              lineColor: '#3179bc'
            },
            tooltip: {
              headerFormat: '',
              pointFormat: 'My Points: {point.y}'
            },
            type: 'scatter'
          }
        ],
        title: {
          text: ''
        },
        tooltip: {
          backgroundColor: '#000',
          distance: 30,
          hideDelay: 100,
          outside: true,
          shadow: false,
          style: {
            color: '#fff'
          },
          useHTML: true
        },
        xAxis: {
          endOnTick: false,
          labels: {
            enabled: false
          },
          lineWidth: 0,
          startOnTick: false,
          tickLength: 0
        },
        yAxis: {
          endOnTick: false,
          gridLineWidth: 0,
          labels: {
            enabled: false
          },
          lineWidth: 0,
          maxPadding: 0,
          minPadding: 0,
          startOnTick: false,
          tickLength: 0,
          title: {
            enabled: false
          }
        }
      }
    },
    refreshLeaderboard() {
      if (this.$currentUser.isAdmin || this.$currentUser.isTeaching || this.$currentUser.sharePoints) {
        this.$loading()
        getLeaderboard().then((data) => {
          this.leaderboard = data
          this.rankLeaderboard()
          this.refreshBoxplot()
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
