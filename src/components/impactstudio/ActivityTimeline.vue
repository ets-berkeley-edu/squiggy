<template>
  <div>
    <div v-if="!eventSeries.length" id="activity-timeline-no-activity-detected">
      No activity detected for this user.
    </div>
    <div v-if="eventSeries.length">
      <div class="d-flex">
        <div id="activity-timeline-legend" class="activity-timeline-legend">
          <div class="activity-timeline-legend-row">
            <div class="activity-timeline-legend-label">
              Contributions
              <div class="activity-timeline-legend-label-explanation">Activities you do</div>
            </div>
            <div class="activity-timeline-legend-bar activity-timeline-blue" />
          </div>
          <div class="activity-timeline-legend-row">
            <div class="activity-timeline-legend-label">
              Impacts
              <div class="activity-timeline-legend-label-explanation">Others responding to your activities</div>
            </div>
            <div class="activity-timeline-legend-bar activity-timeline-red" />
          </div>
        </div>
        <div id="activity-timeline-chart" class="activity-timeline-chart flex-grow-1 flex-shrink-0 mb-0" />
      </div>
      <div class="activity-timeline-footer">
        <div class="mx-4">
          <strong>View by: </strong>
          <button
            id="activity-timeline-view-by-week-btn"
            :class="{'btn-link-disabled': currentZoomPreset === 'week'}"
            :disabled="currentZoomPreset === 'week'"
            @click="zoomPreset('week')"
          >
            Week
          </button> |
          <button
            id="activity-timeline-view-by-month-btn"
            :class="{'btn-link-disabled': currentZoomPreset === 'month'}"
            :disabled="currentZoomPreset === 'month'"
            @click="zoomPreset('month')"
          >
            Month
          </button>
          <span v-if="zoomAllEnabled"> | </span>
          <button
            v-if="zoomAllEnabled"
            id="activity-timeline-view-by-all-btn"
            :class="{'btn-link-disabled': currentZoomPreset === 'all'}"
            :disabled="currentZoomPreset === 'all'"
            @click="zoomPreset('all')"
          >
            All
          </button>
        </div>
        <div>
          <v-btn
            id="activity-timeline-zoom-in-btn"
            outlined
            class="btn-narrow px-3 mx-1"
            @click="zoomRelative(2)"
          >
            +
          </v-btn>
          <v-btn
            id="activity-timeline-zoom-out-btn"
            outlined
            class="btn-narrow px-3 mx-1"
            :disabled="zoomScale === 1.0"
            @click="zoomRelative(0.5)"
          >
            -
          </v-btn>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ActivityTimelineEventDetails from '@/components/impactstudio/ActivityTimelineEventDetails'
import Vue from 'vue'

const ActivityTimelineEventDetailsComponent = Vue.extend(ActivityTimelineEventDetails)

const d3 = require('d3')

const MILLISECONDS_PER_DAY = 1000 * 60 * 60 * 24

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
      arrowOffset: 25,
      currentZoomPreset: null,
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
    drawTimeline() {
      // Draw no timeline if nothing to draw.
      if (!this.eventSeries.length) return
      const chart = document.getElementById('activity-timeline-chart')
      if (!chart) return

      // Clear out any previously drawn timeline.
      this.element = d3.select(chart)
      this.element.selectAll('*').remove()

      // Set initial dimensions and draw container elements.

      const margin = ({top: 0, right: 10, bottom: 0, left: 100})
      const height = 240
      this.timelineWidth = this.element.node().getBoundingClientRect().width

      const svg = this.element.append('svg')
        .attr('height', height + 'px')
        .attr('width', this.timelineWidth + 'px')

      svg
        .append('svg:defs')
        .append('svg:clipPath')
        .attr('id', 'clip-inner')
        .append('svg:rect')
        .attr('id', 'clip-rect-inner')
        .attr('x', 100)
        .attr('y', 0)
        .attr('width', this.timelineWidth - 100 + 'px')
        .attr('height', height + 'px')

      // Define axis behavior.

      const x = d3.scaleTime()
        .domain([this.start, this.end])
        .rangeRound([margin.left, this.timelineWidth - margin.right])

      const x0 = x.copy()

      const y = d3.scalePoint()
        .domain(['actions.engagements', 'actions.interactions', 'actions.creations', 'impacts.engagements', 'impacts.interactions', 'impacts.creations'])
        .rangeRound([0, height+10])
        .padding(1)

      var xAxis = g => g
        .attr('transform', 'translate(0,20)')
        .attr('class', 'activity-timeline-chart-ticks')
        .call(d3.axisTop(x).ticks(8))
        .call(g => g.selectAll('.domain').remove())

      var yAxis = g => g
        .attr('transform', `translate(${margin.left},0)`)
        .attr('class', 'activity-timeline-chart-ticks')
        .call(d3.axisLeft(y).tickFormat(this.translateLabel))
        .call(g => g.selectAll('.tick line').attr('stroke-opacity', 0.1).attr('x2', this.timelineWidth - margin.right - margin.left))
        .call(g => g.selectAll('.domain').remove())

      const xAxisGroup = svg.append('g').call(xAxis)
      const yAxisGroup = svg.append('g').call(yAxis)
      this.activityLabelDetails(yAxisGroup)

      // Plot events.

      svg.append('g')
        .attr('fill', 'none')
        .attr('pointer-events', 'all')
        .attr('clip-path', 'url(#clip-inner)')
        .selectAll('circle')
        .data(this.eventSeries)
        .join('circle')
        .attr('stroke', d => this.$_.startsWith(d.label, 'actions') ? '#8dcffd' : '#fea5a0')
        .attr('r', 5)
        .attr('class', 'event')
        .attr('cx', d => x(d.date))
        .attr('cy', d => y(d.label))
        .on('mouseover', this.showEventDetails)
        .on('mouseout', this.hideEventDetails)

      // Define zoom behavior.

      this.zoom = d3.zoom()
        .scaleExtent([1, 2000])
        .translateExtent([[0, 0], [this.timelineWidth, height]])
        .extent([[0, 0], [this.timelineWidth, height]])
        .on('zoom', function() {
          var transform = d3.event.transform
          x.domain(transform.rescaleX(x0).domain())
          // Redraw x-axis.
          xAxisGroup.call(d3.axisTop(x).ticks(8))
          // Adjust horizontal position of events.
          svg.selectAll('circle.event').attr('cx', d => x(d.date))
          // Store the new zoom scale for future reference.
          this.zoomScale = transform.k
        })

      this.isZoomingToPreset = false

      this.zoom.on('end', () => {
        // All zoom presets should be re-enabled on the next user zoom.
        if (!this.isZoomingToPreset) {
          this.currentZoomPreset = null
        } else {
          this.isZoomingToPreset = false
        }
      })

      // Initial zoom level depends on how much activity there is to see.
      if (this.totalDays <= 7) {
        this.zoomPreset('week', false)
      } else {
        this.zoomPreset('all', false)
      }

      this.element.call(this.zoom)
    },
    fadeout(element) {
      element
        .transition(d3.transition().duration(500))
        .on('end', this.remove)
        .style('opacity', 0)
    },
    hideEventDetails() {
      this.fadeout(d3.select('.details-popover'))
    },
    parseEvents(category) {
      this.$_.forOwn(this.activities[category], (eventSeries, key) => {
        if (eventSeries.length) {
          var firstEventDate = new Date(eventSeries[0].date)
          // If pushing back the start date, set to one day before the first event for visual padding.
          this.start = this.$_.min([this.start, firstEventDate - MILLISECONDS_PER_DAY])
        }
        this.$_.each(eventSeries, e => {
          var event = {label: `${category}.${key}`, ...e}
          event.date = new Date(event.date)
          this.eventSeries.push(event)
        })
      })
    },
    showEventDetails(activity) {
      // Hide any existing event details.
      d3.select('#activity-timeline-chart').selectAll('.details-popover').remove()

      // Format properties for display.
      const displayProperties = {
        activityType: activity.type,
        asset: activity.asset,
        date: d3.timeFormat('%B %d, %Y @ %H:%M')(new Date(activity.date)),
        user: activity.user
      }

      if (activity.asset) {
        displayProperties.title = activity.asset.title
      } else {
        displayProperties.title = this.description
      }

      if (activity.comment && activity.comment.body) {
        displayProperties.comment = activity.comment
        if (activity.comment.body.length > 100) {
          displayProperties.snippet = activity.comment.body.substring(0, 100)
        }
      }

      // The details window starts out hidden...
      var eventDetails = d3
        .select('#activity-timeline-chart')
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
        const eventDetailsComponent = new ActivityTimelineEventDetailsComponent({
          propsData: displayProperties
        })
        eventDetailsComponent.$mount()
        return eventDetailsComponent.$el
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
      var t = this.zoomTransition()
      this.zoom.scaleBy(t, scale)
    },
    zoomTransition(transition) {
      if (transition === false) {
        return this.element
      } else {
        return this.element.transition().duration(300)
      }
    }
  },
  created() {
    // Default to showing at least one week of activity, even if no events go back that far.
    this.start = Date.now() - (7 * MILLISECONDS_PER_DAY)
    this.end = Date.now()

    this.parseEvents('actions')
    this.parseEvents('impacts')

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
    this.drawTimeline()
    d3.select(window).on('resize', this.drawTimeline)
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
  cursor: pointer; /* fallback if grab cursor is unsupported */
  cursor: -moz-grab;
  cursor: -webkit-grab;
  cursor: grab;
}

.activity-timeline-chart-ticks {
  font-size: 14px;
}

.activity-timeline-footer {
  align-items: center;
  display: flex;
  justify-content: right;
  margin-top: 0px;
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

activity-timeline-legend {
  padding-top: 60px;
  width: 124px;
}

.activity-timeline-legend-bar {
  display: table-cell;
  flex: 4px;
}

.activity-timeline-legend-label {
  align-self: center;
  flex: 120px;
  font-size: 13px;
  font-weight: 600;
  padding-right: 10px;
  text-align: left;
}

.activity-timeline-legend-label-explanation {
  font-weight: 300;
}

.activity-timeline-legend-label-small {
  text-align: right;
}

.activity-timeline-legend-row {
  display: flex;
  height: 120px;
  padding: 8px 0;
  width: 124px;
}

.activity-timeline-legend-small {
  display: flex;
  margin: 0 0 15px 120px;
  width: 280px;
}

.activity-timeline-red {
  background-color: #fea5a0;
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
</style>