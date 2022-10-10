<template>
  <div>
    <div class="d-flex">
      <div class="profile-activity-timeline-legend hidden-xs">
        <div class="profile-activity-timeline-legend-row">
          <div class="profile-activity-timeline-legend-label">
            Contributions
            <div class="profile-activity-timeline-legend-label-explanation">Activities you do</div>
          </div>
          <div class="profile-activity-timeline-legend-bar activity-timeline-blue" />
        </div>
        <div class="profile-activity-timeline-legend-row">
          <div class="profile-activity-timeline-legend-label">
            Impacts
            <div class="profile-activity-timeline-legend-label-explanation">Others responding to your activities</div>
          </div>
          <div class="profile-activity-timeline-legend-bar activity-timeline-red" />
        </div>
      </div>
      <div id="activity-timeline-chart" class="flex-grow-1 flex-shrink-0" />
    </div>
    <!-- TODO footer controls don't work yet
    <div class="activity-timeline-footer">
      <div>
        <v-btn @click="zoomRelative(2)">+</v-btn>
        <v-btn :disabled="zoomScale === 1" @click="zoomRelative(0.5)">-</v-btn>
      </div>
      <div>
        <strong>View by:</strong>
        <button
          :class="{'btn-link-disabled': currentZoomPreset === 'week'}"
          :disabled="currentZoomPreset === 'week'"
          @click="zoomPreset('week')"
        >
          Week
        </button> |
        <button
          :class="{'btn-link-disabled': currentZoomPreset === 'month'}"
          :disabled="currentZoomPreset === 'month'"
          @click="zoomPreset('month')"
        >
          Month
        </button>
        <span v-if="zoomAllEnabled">|</span>
        <button
          v-if="zoomAllEnabled"
          :class="{'btn-link-disabled': currentZoomPreset === 'all'}"
          :disabled="currentZoomPreset === 'all'"
          @click="zoomPreset('all')"
        >
          All
        </button>
      </div>
    </div>
    -->
    <div id="activity-timeline-contributions" class="mb-3">
      <h3>Contributions (activities you do)</h3>
      <div>
        <h4>Views/Likes</h4>
        <div id="activity-timeline-actions-engagements" />
        <div>
          {{ activities.actions.engagements }}
        </div>
        <h4>Interactions</h4>
        <div id="activity-timeline-actions-interactions" />
        <div>
          {{ activities.actions.interactions }}
        </div>
        <h4>Creations</h4>
        <div id="activity-timeline-actions-creations" />
        <div>
          {{ activities.actions.creations }}
        </div>
      </div>
    </div>
    <div id="activity-timeline-impacts" class="mb-3">
      <h3>Impacts (others responding to your activities)</h3>
      <div>
        <h4>Views/Likes</h4>
        <div id="activity-timeline-impacts-engagements" />
        <div>
          {{ activities.impacts.engagements }}
        </div>
        <h4>Interactions</h4>
        <div id="activity-timeline-impacts-interactions" />
        <div>
          {{ activities.impacts.interactions }}
        </div>
        <h4>Reuses</h4>
        <div id="activity-timeline-impacts-creations" />
        <div>
          {{ activities.impacts.creations }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
const d3 = require('d3')

export default {
  name: 'ActivityTimeline',
  props: {
    activities: {
      required: true,
      type: Object,
    }
  },
  data() {
    return {
      activity: null,
      arrowOffset: 25,
      currentZoomPreset: null,
      display: {},
      element: null,
      eventSeries: [],
      isZoomingToPreset: false,
      maxZoom: null,
      timelineWidth: null,
      totalDays: null,
      zoom: null,
      zoomAllEnabled: null,
      zoomScale: null,
    }
  },
  methods: {
    activityLabelDetails(yAxisGroup) {
      yAxisGroup.selectAll('.tick text')
        .classed('activity-timeline-label-hoverable', true)
        .on('mouseover', label => {
          console.log('mouse over')

          var pageX = d3.event.pageX
          var pageY = d3.event.pageY

          var eventDetails = d3
            .select('#activity-timeline-chart')
            .append('div')
            .classed('details-popover', true)
            .classed('details-popover-label', true)
            .style('opacity', 0)

          var eventDetailsDimensions = eventDetails.node().getBoundingClientRect()
          eventDetails.style('left', (pageX - this.arrowOffset + 'px'))
            .style('top', (pageY - (eventDetailsDimensions.height + 16) + 'px'))
            .classed('left', true)

          var detailsDiv = document.createElement('div')
          // TODO add template HTML
          detailsDiv.innerHTML = '<div class="profile-activity-breakdown-popover-outer">'
          detailsDiv.innerHTML += `<h4 class="profile-activity-breakdown-header">${this.translateLabel(label)}</h4>`
          detailsDiv.innerHTML += '<div class="profile-activity-breakdown-popover-details">'
          if (label === 'actions.engagements' || label === 'impacts.engagements') {
            detailsDiv.innerHTML += 'Includes the activities: views and likes.'
          } else if (label === 'actions.interactions' || label === 'impacts.interactions') {
            detailsDiv.innerHTML += 'Includes the activities: comments and discussion posts.'
          } else if (label === 'actions.creations') {
            detailsDiv.innerHTML += 'Includes the activities: add new assets, add assets to whiteboard, export whiteboards, and remix whiteboards.'
          } else if (label === 'impacts.creations') {
            detailsDiv.innerHTML += 'Includes the activities: asset used in whiteboards and whiteboard remixed.'
          }
          detailsDiv.innerHTML += '</div></div>'
          eventDetails.append(() => detailsDiv)
          eventDetails.style('opacity', 1)
        })
        .on('mouseout', () => {
          d3.select('#activity-timeline-chart').selectAll('.details-popover').remove()
        })
    },
    drawTimeline(element) {
      this.element = d3.select(element)
      this.element.selectAll('*').remove()

      var margin = ({top: 0, right: 10, bottom: 10, left: 100})
      var height = 260
      this.timelineWidth = this.element.node().getBoundingClientRect().width

      var y = d3.scalePoint()
        .domain(['actions.engagements', 'actions.interactions', 'actions.creations', 'impacts.engagements', 'impacts.interactions', 'impacts.creations'])
        .rangeRound([margin.top, height - margin.bottom])
        .padding(1)

      var x = d3.scaleTime()
        .domain([this.start, this.end])
        .rangeRound([margin.left + 10, this.timelineWidth - margin.right])

      var yAxis = g => g
        .attr('transform', `translate(${margin.left},0)`)
        .attr('class', 'activity-timeline-chart-ticks')
        .call(d3.axisLeft(y).tickFormat(this.translateLabel))
        .call(g => g.selectAll('.tick line').clone().attr('stroke-opacity', 0.1).attr('x2', this.timelineWidth - margin.right - margin.left))
        .call(g => g.selectAll('.domain').remove())

      var xAxis = g => g
        .attr('transform', 'translate(0,20)')
        .attr('class', 'activity-timeline-chart-ticks')
        .call(d3.axisTop(x).ticks(8))
        .call(g => g.selectAll('.tick line').clone().attr('stroke-opacity', 0.1).attr('y2', height - margin.bottom - margin.top))
        .call(g => g.selectAll('.domain').remove())

      const svg = this.element.append('svg')
        .attr('height', height + 'px')
        .attr('width', this.timelineWidth + 'px')

      svg.append('g').call(xAxis)

      const yAxisGroup = svg.append('g').call(yAxis)
      this.activityLabelDetails(yAxisGroup)

      const timeFormat = d3.timeFormat('%c')

      svg.append('g')
        .attr('fill', 'none')
        .attr('pointer-events', 'all')
        .selectAll('circle')
        .data(this.eventSeries)
        .join('circle')
        .attr('stroke', d => this.$_.startsWith(d.label, 'actions') ? '#8dcffd' : '#fea5a0')
        .attr('r', 5)
        .attr('cx', d => x(d.date))
        .attr('cy', d => y(d.label))
        .append('title')
        .text(d => ` ${d.type} ${timeFormat(d.date)}`)

      this.zoom = d3.zoom()

      this.isZoomingToPreset = false

      this.zoom.on('end', () => {
        // All zoom presets should be re-enabled on the next user zoom.
        if (!this.isZoomingToPreset) {
          this.currentZoomPreset = null
        } else {
          this.isZoomingToPreset = false
        }
        // Update with the current zoom scale.
        this.zoomScale = d3.zoomTransform(this.element.select('.chart-wrapper').node()).k
      })

      // Initial zoom level depends on how much activity there is to see.
      if (this.totalDays <= 7) {
        this.zoomPreset('week', false)
      } else {
        this.zoomPreset('all', false)
      }
    },
    fadeout(element) {
      element.transition(d3.transition().duration(500))
        .on('end', this.remove)
        .style('opacity', 0)
    },
    hideEventDetails() {
      this.fadeout(d3.select('.details-popover'))
    },
    showEventDetail(activity) {
      // Hide any existing event details.
      d3.select('.activity-timeline-chart').selectAll('.details-popover').remove()

      this.activity = activity

      // Format properties for display.
      this.display = {
        'date': d3.timeFormat('%B %d, %Y @ %H:%M')(new Date(activity.date))
      }

      if (activity.asset) {
        this.display.title = activity.asset.title
      } else {
        this.display.title = this.description
      }

      if (activity.comment && activity.comment.body) {
        this.display.comment = true
        if (activity.comment.body.length > 100) {
          this.display.snippet = activity.comment.body.substring(0, 100)
        }
      }

      // The details window starts out hidden...
      var eventDetails = d3
        .select('.activity-timeline-chart')
        .append('div')
        .classed('details-popover', true)
        .classed('details-popover-activity', true)
        .style('opacity', 0)

      // ...and transitions to visible.
      eventDetails
        .transition(d3.transition().duration(100).ease(d3.easeLinear))
        .on('start', () => {
          eventDetails.style('display', 'block')
        })
        .style('opacity', 1)

      // The location of the arrow element depends on which side of the chart we're on.
      var pageX = d3.event.pageX
      var pageY = d3.event.pageY

      var eventDetailsDimensions = eventDetails.node().getBoundingClientRect()

      var direction = pageX > eventDetailsDimensions.width ? 'right' : 'left'

      var left = direction === 'right' ?
        pageX - eventDetailsDimensions.width + this.arrowOffset :
        pageX - this.arrowOffset

      eventDetails
        .style('left', (left + 'px'))
        .style('top', (pageY - (eventDetailsDimensions.height + 16) + 'px'))
        .classed(direction, true)

      eventDetails.append(() => {
        var detailsDiv = document.createElement('div')
        // TODO add template HTML
        detailsDiv.innerHTML = 'No event details yet'
        return detailsDiv
      })

      // Cancel pending fadeout if hovering over detail window.
      eventDetails.on('mouseenter', () => {
        eventDetails.transition()
      })

      // Restart fadeout after leaving detail window.
      eventDetails.on('mouseleave', () => {
        this.fadeout(eventDetails)
      })
    },
    translateLabel(label) {
      return this.$_.get({
        actions: {
          engagements: 'Views/Likes',
          interactions: 'Interactions',
          creations: 'Creations'
        },
        impacts: {
          engagements: 'Views/Likes',
          interactions: 'Interactions',
          creations: 'Reuses'
        }
      }, label)
    },
    zoomDays(days, transition) {
      var scaleFactor = this.maxZoom / days
      var translateX = (1 - scaleFactor) * this.timelineWidth
      var transform = d3.zoomIdentity.translate(translateX, 0).scale(scaleFactor)
      this.zoomTransition(transition).call(this.zoom.transform, transform)
    },
    zoomPreset(preset, transition) {
      this.isZoomingToPreset = true
      switch (preset) {
      case 'week':
        this.zoomDays(7, transition)
        break
      case 'month':
        this.zoomDays(30, transition)
        break
      case 'all':
        this.zoomTransition(transition).call(this.zoom.transform, d3.zoomIdentity)
        break
      default:
      }
      // Disable whichever zoom preset button was just clicked.
      this.currentZoomPreset = preset
    },
    zoomRelative(scale) {
      this.zoomTransition().call(this.zoom.scaleBy, scale)
    },
    zoomTransition(transition) {
      var wrapper = this.element.select('.chart-wrapper')
      if (transition === false) {
        return wrapper
      } else {
        return wrapper.transition().duration(300)
      }
    }
  },
  created() {
    const MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24

    // Default to showing at least one week of activity, even if no events go back that far.
    this.start = Date.now() - (7 * MILLISECONDS_PER_DAY)
    this.end = Date.now()

    this.$_.forOwn(this.activities.actions, (eventSeries, key) => {
      if (eventSeries.length) {
        var firstEventDate = new Date(eventSeries[0].date)
        this.start = this.$_.min([this.start, firstEventDate])
      }
      this.$_.each(eventSeries, e => {
        var event = {label: `actions.${key}`, ...e}
        event.date = new Date(event.date)
        this.eventSeries.push(event)
      })
    })
    this.$_.forOwn(this.activities.impacts, (eventSeries, key) => {
      if (eventSeries.length) {
        var firstEventDate = new Date(eventSeries[0].date)
        this.start = this.$_.min([this.start, firstEventDate])
      }
      this.$_.each(eventSeries, e => eventSeries.push({label: `impacts.${key}`, ...e}))
    })

    this.totalDays = parseFloat(this.end - this.start) / MILLISECONDS_PER_DAY

    // If there's more than a month of activity, enable the 'all' zoom option.
    if (this.totalDays > 30) {
      this.zoomAllEnabled = true
      this.maxZoom = this.totalDays
    // Otherwise set maximum zoom-out to the past month.
    } else {
      this.zoomAllEnabled = false
      this.maxZoom = 30
      this.start = Date.now() - (30 * MILLISECONDS_PER_DAY)
    }
  },
  mounted() {
    this.drawTimeline(document.getElementById('activity-timeline-chart'))

    // Redraw the timeline when the window is resized.
    d3.select(window).on('resize', () => {
      this.drawTimeline(document.getElementById('activity-timeline-chart'))
    })
  }
}
</script>

<style>
.activity-timeline {
  flex: 1;
  margin-bottom: 75px;
}

.activity-timeline-blue {
  background-color: #8dcffd;
}

.activity-timeline .btn-link {
  border: 0;
  padding: 0 2px;
  vertical-align: bottom;
}

.activity-timeline .btn-link-disabled {
  color: #777;
  cursor: default;
}

.activity-timeline-chart {
  flex: 1;
}

.activity-timeline-chart-ticks {
  font-size: 14px;
}

.activity-timeline-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 15px;
  padding-left: 130px;
}

.activity-timeline-label {
  font-size: 13px;
  font-weight: 300;
}

.activity-timeline-label-hoverable {
  cursor: pointer;
  fill: #4172b4;
}

.activity-timeline-red {
  background-color: #fea5a0;
}

.chart-wrapper {
  cursor: pointer; /* fallback if grab cursor is unsupported */
  cursor: -moz-grab;
  cursor: -webkit-grab;
  cursor: grab;
}

.details-popover {
  background: #fff;
  border: 1px solid #aaa;
  border-radius: 6px;
  box-shadow: 0 5px 10px rgba(0,0,0,.2);
  -webkit-box-shadow: 0 5px 10px rgba(0,0,0,.2);
  left: none;
  max-width: 480px;
  outline: 0;
  padding: 10px;
  position: absolute;
  width: 480px;
}

.details-popover::after {
  background: #fff;
  border: 1px solid #aaa;
  border-width: 0 1px 1px 0;
  content: '';
  display: block;
  height: 10px;
  position: absolute;
  transform: rotate(45deg);
  width: 10px;
  z-index: 1;
}

.details-popover-activity {
  height: 142px;
}

.details-popover-activity::after {
  top: 136px;
}

.details-popover-label {
  height: 90px;
}

.details-popover-label::after {
  top: 84px;
}

.details-popover.left::after {
  left: 15px;
}

.details-popover.right::after {
  right: 15px;
}

.details-popover .details-popover-avatar {
  background: #fff;
  border: 1px solid #c2c8d0;
  border-radius: 100%;
  overflow: hidden;
}

.details-popover .details-popover-avatar img {
  height: 100%;
  width: 100%;
}

.details-popover .details-popover-avatar-large {
  flex: 0 0 100px;
  height: 100px;
  margin-right: 15px;
  width: 100px;
}

.details-popover .details-popover-avatar-small {
  height: 50px;
  left: 65px;
  position: absolute;
  top: 65px;
  width: 50px;
}

.details-popover .details-popover-comment {
  font-style: italic;
}

.details-popover .details-popover-container {
  display: flex;
  flex-direction: row;
  position: relative;
  z-index: 2;
}

.details-popover .details-popover-description {
  color: #777;
  font-size: 13px;
}

.details-popover .details-popover-strong {
  font-size: 14px;
  font-weight: 600;
}

.details-popover .details-popover-thumbnail {
  border: 1px solid #c2c8d0;
  height: 100px;
  margin: 1px 25px 15px 1px;
  width: 100px;
}

.details-popover .details-popover-thumbnail-default {
  align-items: center;
  background-color: #E8E8E8;
  display: flex;
  justify-content: center;
}

.details-popover .details-popover-thumbnail-default i {
  color: #ADABAA;
  font-size: 50px;
}

.details-popover .details-popover-timestamp {
  color: #777;
  font-size: 12px;
}

.details-popover .details-popover-title {
  font-size: 15px;
  margin-bottom: 10px;
}

profile-activity-timeline-legend {
  padding-top: 60px;
  width: 124px;
}

.profile-activity-timeline-legend-bar {
  display: table-cell;
  flex: 4px;
}

.profile-activity-timeline-legend-label {
  align-self: center;
  flex: 120px;
  font-size: 13px;
  font-weight: 600;
  padding-right: 10px;
  text-align: left;
}

.profile-activity-timeline-legend-label-explanation {
  font-weight: 300;
}

.profile-activity-timeline-legend-label-small {
  text-align: right;
}

.profile-activity-timeline-legend-row {
  display: flex;
  height: 120px;
  padding: 8px 0;
  width: 124px;
}

.profile-activity-timeline-legend-small {
  display: flex;
  margin: 0 0 15px 120px;
  width: 280px;
}
</style>