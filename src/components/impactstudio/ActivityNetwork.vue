<template>
  <div class="profile-activity-network-container">
    <div v-if="minScale !== 1" class="profile-activity-network-controls-outer">
      <div>
        <strong>View:</strong>
        <span v-if="meNode">
          <button
            class="profile-activity-network-preset"
            :class="{'profile-activity-network-preset-disabled': currentNetworkPreset === 'me'}"
            :disabled="currentNetworkPreset === 'me'"
            @click="networkPresent('me')"
          >
            Me
          </button> |
        </span>
        <button
          class="profile-activity-network-preset"
          :class="{'profile-activity-network-preset-disabled': zoomScale === minScale}"
          :disabled="zoomScale === minScale"
          @click="networkPreset('all')"
        >
          All networks
        </button>
      </div>
      <div>
        <button @click="networkZoom(1.25)">+</button>
        <button @click="networkZoom(0.8)">-</button>
      </div>
    </div>
    <svg id="profile-activity-network" class="profile-activity-network" clip-path="url('#profile-activity-network-clipper')"></svg>
    <div id="profile-activity-network-controls-outer-bottom" class="profile-activity-network-controls-outer">
      <form id="profile-activity-network-controls" class="profile-activity-network-controls">
        <div class="profile-activity-network-controls-title">Collaboration activities:</div>
        <label v-for="(type, label) in interactionTypesEnabled" :key="label" class="profile-activity-network-controls-label">
          <input v-model="interactionTypesEnabled[label]" type="checkbox" @change="restartLinks">
          {{ label }}
        </label>
      </form>
      <div class="profile-activity-network-controls-show-users">
        <button
          class="profile-activity-network-preset"
          :class="{'profile-activity-network-preset-disabled': showUsers === 'recent'}"
          :disabled="showUsers === 'recent'"
          @click="setShowUsers('recent')"
        >
          Last {{ recentUserCutoff }} Days
        </button> |
        <button
          class="profile-activity-network-preset"
          :class="{'profile-activity-network-preset-disabled': showUsers === 'all'}"
          :disabled="showUsers === 'all'"
          @click="setShowUsers('all')"
        >
          All
        </button>
      </div>
    </div>
  </div>
</template>

<script>
const d3 = require('d3')

import CanvasConversation from '@/mixins/CanvasConversation'
import Context from '@/mixins/Context'

export default {
  name: 'ActivityNetwork',
  mixins: [CanvasConversation, Context],
  props: {
    courseInteractions: {
      required: true,
      type: Array,
    },
    user: {
      required: true,
      type: Object
    },
    users: {
      required: true,
      type: Array
    }
  },
  data() {
    return {
      activityNetworkScale: 400,
      bounds: [],
      clipPathRect: undefined,
      container: undefined,
      controlsForm: undefined,
      currentNetworkPreset: 'me',
      defaultRadius: 10,
      defs: undefined,
      interactions: {
        links: [],
        linkTypes: this.courseInteractions,
        allUsers: [],
        recentUsers: [],
        recentIds: {}
      },
      interactionTypes: {
        'Views': ['get_asset_view'],
        'Likes': ['get_asset_like'],
        'Comments': ['get_asset_comment_reply', 'get_asset_comment'],
        'Posts': ['get_discussion_entry_reply'],
        'Assets Added to Whiteboard': ['get_whiteboard_add_asset'],
        'Remixes': ['get_whiteboard_remix'],
        'Whiteboards Exported': ['co_create_whiteboard']
      },
      interactionTypesEnabled: {},
      isZoomingToPreset: false,
      linksByIds: {},
      linkSelection: undefined,
      linkTypesVisible: {},
      meNode: null,
      minScale: 1,
      nodeSelection: undefined,
      recentUserCutoff: 45,
      showUsers: 'recent',
      simulation: undefined,
      svg: undefined,
      viewportHeight: undefined,
      viewportWidth: undefined,
      zoom: undefined,
      zoomScale: 1
    }
  },
  methods: {
    avatar(d) {
      var avatarId = 'avatar_' + d.id
      this.defs.append('svg:pattern')
        .attr('id', avatarId)
        .attr('width', '100%')
        .attr('height', '100%')
        .attr('patternContentUnits', 'objectBoundingBox')
        .append('svg:image')
        .attr('xlink:href', d.canvasImage)
        .attr('width', 1)
        .attr('height', 1)
        .attr('preserveAspectRatio', 'none')
      return 'url(#' + avatarId + ')'
    },
    calculateLinks() {
      this.$_.forOwn(this.interactionTypesEnabled, (isEnabled, key) => {
        this.$_.forEach(this.interactionTypes[key], (interactionType) => {
          this.linkTypesVisible[interactionType] = isEnabled
        })
      })

      this.$_.forEach(this.$_.keys(this.linksByIds), key => {
        delete this.linksByIds[key]
      })

      // To ease selection logic, we explicitly link each node to itself.
      this.$_.forEach(this.interactions.nodes, node => {
        this.linksByIds[node.id + ',' + node.id] = {'total': 1}
      })

      this.$_.forEach(this.interactions.linkTypes, link => {
        if (!this.linkTypesVisible[link.type]) {
          return
        }

        if (this.showUsers === 'recent' &&
          (!this.interactions.recentIds[link.source] || !this.interactions.recentIds[link.target])) {
          return
        }

        var linkKey
        var direction
        if (link.source < link.target) {
          linkKey = link.source + ',' + link.target
          direction = 'up'
        } else {
          linkKey = link.target + ',' + link.source
          direction = 'down'
        }
        this.linksByIds[linkKey] = this.linksByIds[linkKey] || {}
        this.linksByIds[linkKey].total = this.linksByIds[linkKey].total || 0
        this.linksByIds[linkKey].total += link.count
        this.linksByIds[linkKey][direction] = this.linksByIds[linkKey][direction] || {}
        this.linksByIds[linkKey][direction][link.type] = this.linksByIds[linkKey][direction][link.type] || 0
        this.linksByIds[linkKey][direction][link.type] += link.count
      })

      this.interactions.links.splice(0, this.interactions.links.length)

      this.$_.forOwn(this.linksByIds, (value, key) => {
        var keyComponents = key.split(',')
        var taperedTotal = value.total === 0 ? 0 : Math.round(1 + Math.sqrt(value.total - 1))
        this.interactions.links.push({
          'source': keyComponents[0],
          'target': keyComponents[1],
          'value': taperedTotal
        })
      })
    },
    fadeout(element) {
      // Fade out an element (used for user details tooltip).
      element.transition(d3.transition().duration(500))
        .on('end', function() {
          this.remove()
        })
        .style('opacity', 0)
    },
    isLinkConnected(link) {
      return this.focalUser.id === link.source.id || this.focalUser.id === link.target.id
    },
    isNodeConnected(node) {
      var key1 = this.focalUser.id + ',' + node.id
      var key2 = node.id + ',' + this.focalUser.id
      return !!(this.linksByIds[key1] && this.linksByIds[key1].total) || !!(this.linksByIds[key2] && this.linksByIds[key2].total)
    },
    networkPreset(preset) {
      this.isZoomingToPreset = true
      this.currentNetworkPreset = preset
      if (preset === 'me') {
        var translateX = Math.max(this.bounds[0][0], Math.min(this.viewportWidth / 2 - this.meNode.x, this.bounds[1][0] - this.viewportWidth))
        var translateY = Math.max(this.bounds[0][1], Math.min(this.viewportHeight / 2 - this.meNode.y, this.bounds[1][1] - this.viewportHeight))
        this.svg.transition().duration(300).call(this.zoom.transform, d3.zoomIdentity.translate(translateX, translateY))
      } else if (preset === 'all') {
        this.svg.transition().duration(300).call(this.zoom.scaleTo, this.minScale)
      }
    },
    networkZoom(scale) {
      this.svg.transition().duration(300).call(this.zoom.scaleBy, scale)
    },
    onNodeDeselected() {
      // Node deselection handler; remove tooltip, restore opacity to all nodes.
      this.fadeout(this.container.select('.profile-activity-network-tooltip'))
      this.nodeSelection.style('opacity', 1)
      this.linkSelection.style('opacity', link => {
        return this.isLinkConnected(link) ? 1 : 0.3
      })
    },
    onNodeSelected(node) {
      // Node selection handler; show connections and tooltip.
      if (!node) {
        node = d3.select(this).node().__data__
      }
      this.selectedUser = node

      if (this.isNodeConnected(this.selectedUser)) {
        this.showConnections()
      }

      // Clear any existing tooltips.
      this.container.selectAll('.profile-activity-network-tooltip').remove()

      var coordinates = [0, 0]
      coordinates = d3.mouse(this.container.node())
      var mouseX = coordinates[0]
      var mouseY = coordinates[1]

      // Calculate interaction totals between the selected users.
      var interactionsLeft
      var interactionsRight
      var linksBetweenUsers
      if (this.focalUser.id < this.selectedUser.id) {
        linksBetweenUsers = this.linksByIds[this.focalUser.id + ',' + this.selectedUser.id]
        if (linksBetweenUsers) {
          interactionsLeft = linksBetweenUsers.up || {}
          interactionsRight = linksBetweenUsers.down || {}
        }
      } else if (this.focalUser.id > this.selectedUser.id) {
        linksBetweenUsers = this.linksByIds[this.selectedUser.id + ',' + this.focalUser.id]
        if (linksBetweenUsers) {
          interactionsLeft = linksBetweenUsers.down || {}
          interactionsRight = linksBetweenUsers.up || {}
        }
      }

      if (interactionsLeft || interactionsRight) {
        this.interactionCounts = {
          'left': {},
          'right': {}
        }
        this.$_.forOwn(this.interactionTypes, (typesList, interactionLabel) => {
          this.interactionCounts.left[interactionLabel] = 0
          this.interactionCounts.right[interactionLabel] = 0
          this.$_.forEach(typesList, typeKey => {
            var leftCount = (interactionsLeft[typeKey] || 0)
            var rightCount = (interactionsRight[typeKey] || 0)
            // Whiteboard co-creation is a special-case bidirectional activity.
            if (typeKey === 'co_create_whiteboard') {
              var totalCount = leftCount + rightCount
              leftCount = totalCount
              rightCount = totalCount
            }
            this.interactionCounts.left[interactionLabel] += leftCount
            this.interactionCounts.right[interactionLabel] += rightCount
          })
        })
      } else {
        this.interactionCounts = null
      }

      // Position tooltip and arrow; orientation will depend on location within the chart.
      var containerDimensions = this.container.node().getBoundingClientRect()
      var tooltipOrientation = (mouseX < 240) ? 'left' : 'right'

      var tooltip = this.container.append('div')
        .attr('class', ('profile-activity-network-tooltip profile-activity-network-tooltip-' + tooltipOrientation))
        .style('bottom', (containerDimensions.height - mouseY + 16) + 'px')

      if (tooltipOrientation === 'left') {
        tooltip.style('left', (mouseX - 30) + 'px')
      } else {
        tooltip.style('right', (containerDimensions.width - mouseX - 30) + 'px')
      }

      // The tooltip starts out hidden...
      tooltip.style('opacity', 0)
      tooltip.append(function() {
        var tooltipDiv = document.createElement('div')
        // TODO Compile tooltip template
        tooltipDiv.innerHTML = 'No tooltip yet.'
        // tooltipDiv.innerHTML = $templateCache.get('/app/dashboard/activityNetworkTooltip.html')
        // $compile(tooltipDiv)(this)
        return tooltipDiv
      })

      // ...and transitions to visible.
      tooltip.transition(d3.transition().duration(100).ease(d3.easeLinear))
        .on('start', () => {
          tooltip.style('display', 'block')
        })
        .style('opacity', 1)

      // Cancel pending fadeout if hovering over tooltip.
      tooltip.on('mouseenter', () => {
        tooltip.transition()
      })

      // Restart fadeout after leaving tooltip.
      tooltip.on('mouseleave', () => {
        this.fadeout(tooltip)
      })
    },
    resetNodes() {
      if (this.showUsers === 'recent') {
        this.interactions.nodes = this.interactions.recentUsers
      } else {
        this.interactions.nodes = this.interactions.allUsers
      }
      // Size force diagram to window, accounting for course size and resizing as necessary.
      this.activityNetworkScale = Math.round(Math.sqrt(4000 * this.interactions.nodes.length))
    },
    restart(alpha, recalculateConnections) {
      this.calculateLinks()

      this.linkSelection = this.linkSelection.data(this.interactions.links)
      this.linkSelection.exit().remove()

      this.nodeSelection = this.nodeSelection.data(this.interactions.nodes)
      this.nodeSelection.exit().remove()
      this.svg.selectAll('circle').remove()
      this.svg.selectAll('text').remove()

      this.simulation.on('tick', this.ticked)
      this.simulation.nodes(this.interactions.nodes)
      this.simulation.force('link').links(this.interactions.links)

      this.linkSelection = this.linkSelection.enter().append('line')
        .attr('stroke', 'black')
        .merge(this.linkSelection)

      this.nodeSelection = this.nodeSelection.enter().append('g')
        .attr('class', 'node')
        .merge(this.nodeSelection)
      this.nodeSelection.attr('id', d => {
        return 'profile-activity-network-user-node-' + d.id
      })
      this.nodeSelection.append('circle')
        .attr('r', d => {
          if (d.id === this.focalUser.id) {
            return 25
          } else {
            return this.defaultRadius
          }
        })
        .on('mouseover', this.onNodeSelected)
        .on('mouseout', this.onNodeDeselected)
        .on('click', node => {
          this.container.select('.profile-activity-network-tooltip').remove()
          this.focalUser = node
          this.onNodeSelected(node)
          this.restart(0.1, false)
        })
      this.nodeSelection.append('text')
        .attr('dx', 0)
        .attr('dy', d => {
          if (d.id === this.focalUser.id) {
            return 35
          } else {
            return 25
          }
        })
        // Only first names fit easily on the force diagram.
        .text(d => {
          return d.canvasFullName.split(' ')[0]
        })

      // Calculate links to highlight the focal user's connections, but not in full mouseover mode.
      if (recalculateConnections) {
        this.showConnections()
        this.onNodeDeselected()
      }

      this.simulation.alpha(alpha).restart()
    },
    restartLinks() {
      this.restart(0.1, true)
    },
    setShowUsers(showUsers) {
      this.showUsers = showUsers
      this.sizeAndRestart(0.1)
    },
    showConnections() {
      this.nodeSelection.attr('class', node => {
        var classAttr
        if (this.isNodeConnected(node)) {
          classAttr = 'node node-connected'
        } else {
          classAttr = 'node node-unconnected'
        }
        if (node.id === this.$currentUser.id) {
          this.meNode = node
          classAttr += ' node-me'
        } else if (node.looking_for_collaborators) {
          classAttr += ' node-looking-for-collaborators'
        }
        return classAttr
      })
      this.nodeSelection.style('fill', node => {
        if (this.isNodeConnected(node)) {
          return this.avatar(node)
        } else {
          return '#eee'
        }
      })
      this.nodeSelection.style('opacity', node => {
        return this.isNodeConnected(node) ? 1 : 0.35
      })
      this.linkSelection.style('opacity', link => {
        return this.isLinkConnected(link) ? 1 : 0.15
      })
      this.linkSelection.style('stroke-width', link => {
        return this.isLinkConnected(link) ? link.value : 1
      })
    },
    sizeAndRestart(recalculateConnections) {
      this.resetNodes()

      this.viewportWidth = this.controlsForm.node().getBoundingClientRect().width
      this.viewportHeight = Math.max(300, Math.min(700, this.activityNetworkScale))

      var aspectRatio = this.viewportWidth * 1.0 / this.viewportHeight

      this.svg.attr('width', this.viewportWidth).attr('height', this.viewportHeight)
      this.clipPathRect.attr('width', this.viewportWidth).attr('height', this.viewportHeight)

      var xMargin = Math.max(0, (Math.round(this.activityNetworkScale * aspectRatio) - this.viewportWidth) / 2)
      var yMargin = Math.max(0, (this.activityNetworkScale - this.viewportHeight) / 2)
      this.bounds = [[-1 * xMargin, -1 * yMargin], [this.viewportWidth + xMargin, this.viewportHeight + yMargin]]
      this.minScale = Math.min(this.viewportHeight / this.activityNetworkScale, 1)
      this.zoom.scaleExtent([this.minScale, 1]).translateExtent(this.bounds)

      this.simulation.force('charge', d3.forceManyBody().strength(-0.3 * this.activityNetworkScale).distanceMax(300))
      this.simulation.force('gravity', d3.forceManyBody().strength(70).distanceMax(600))
      this.simulation.force('center', d3.forceCenter(this.viewportWidth / 2, this.viewportHeight / 2))
      this.simulation.force('collide', d3.forceCollide(30))
      this.restart(0.6, recalculateConnections)
    },
    ticked() {
      this.linkSelection
        .attr('x1', function(d) { return d.source.x })
        .attr('y1', function(d) { return d.source.y })
        .attr('x2', function(d) { return d.target.x })
        .attr('y2', function(d) { return d.target.y })

      this.svg.selectAll('circle')
        .attr('cx', d => {
          if (d.id === this.user.id) {
            return d.x = Math.max((this.viewportWidth - 200) / 2, Math.min((this.viewportWidth + 200) / 2, d.x))
          } else if (d.id === this.focalUser.id) {
            return d.x = Math.max(this.bounds[0][0] + 40, Math.min(this.bounds[1][0] - 40, d.x))
          } else {
            return d.x = Math.max(this.bounds[0][0] + this.defaultRadius + 15, Math.min(this.bounds[1][0] - (this.defaultRadius + 15), d.x))
          }
        })
        .attr('cy', d => {
          if (d.id === this.user.id) {
            return d.y = Math.max((this.viewportHeight - 200) / 2, Math.min((this.viewportHeight + 200) / 2, d.y))
          } else if (d.id === this.focalUser.id) {
            return d.y = Math.max(this.bounds[0][1] + 30, Math.min(this.bounds[1][1] - 45, d.y))
          } else {
            return d.y = Math.max(this.bounds[0][1] + this.defaultRadius + 5, Math.min(this.bounds[1][1] - (this.defaultRadius + 20), d.y))
          }
        })

      this.svg.selectAll('text')
        .attr('x', function(d) { return d.x })
        .attr('y', function(d) { return d.y })
    }
  },
  mounted() {
    this.$_.each(this.users, user => {
      if (user.canvasCourseRole === 'Student' || user.canvasCourseRle === 'Learner') {
        this.interactions.allUsers.push(user)
        var lastActiveOrCreated = user.lastActivity || user.createdAt
        if (lastActiveOrCreated &&
          // Recent user cutoff is expressed in days, date difference in milliseconds.
          ((new Date() - new Date(lastActiveOrCreated)) / 86400000 < this.recentUserCutoff)) {
          this.interactions.recentUsers.push(user)
          this.interactions.recentIds[user.id] = true
        }
      }
    })

    this.interactionTypesEnabled = this.$_.mapValues(this.interactionTypes, this.$_.constant(true))
    this.showUsers = this.interactions.recentUsers.length > 1 ? 'recent' : 'all'

    // Initialize force diagram.
    this.svg = d3.select('#profile-activity-network')
    this.container = d3.select('.profile-activity-network-container')
    this.controlsForm = d3.select('#profile-activity-network-controls-outer-bottom')

    this.simulation = d3.forceSimulation()
    this.simulation.force('link', d3.forceLink().id(d => d.id))
    this.simulation.alphaDecay(0.05)

    this.resetNodes()

    // Set the focal user, whose avatar will appear larger and who will be the point of reference for interaction counts.
    this.focalUser = this.user

    // The selected user is set on mouseover.
    this.selectedUser = this.focalUser

    // Clear any existing elements within the SVG and re-initialize.
    this.svg.selectAll('g').remove()
    this.svg.selectAll('defs').remove()
    this.defs = this.svg.append('defs')
    var g = this.svg.append('g')

    this.linkSelection = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
    this.nodeSelection = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g.circle')
    this.clipPathRect = this.defs.append('clipPath')
      .attr('id', 'profile-activity-network-clipper')
      .append('rect')

    var executeZoom = () => {
      g.attr('transform', d3.event.transform)
    }
    this.zoom = d3.zoom().on('zoom', executeZoom)
    this.svg.call(this.zoom)

    this.zoom.on('end', () => {
      // All zoom presets should be re-enabled on the next user zoom.
      if (!this.isZoomingToPreset) {
        this.currentNetworkPreset = null
      } else {
        this.isZoomingToPreset = false
      }
      // Update the scope with the current zoom scale.
      this.zoomScale = d3.zoomTransform(this.svg.node()).k
    })

    // Touch devices have no 'mouseout' event; call the deselection handler when document elements are tapped.
    if ('ontouchstart' in window) {
      document.body.addEventListener('touchstart', this.onNodeDeselected)
    }

    window.addEventListener('resize', () => {
      this.sizeAndRestart(false)
    })

    // Handle user profile loads triggered from a tooltip link.
    this.switchUser = function(user) {
      this.container.select('.profile-activity-network-tooltip').remove()
      this.loadProfileById(user.id, false, true)
    }

    this.sizeAndRestart(true)
  }
}
</script>

<style>
.profile-activity-network {
  border: 1px solid #ccc;
  min-width: 100%;
}

.profile-activity-network .links line {
  opacity: 0.3;
  stroke: #999;
}

.profile-activity-network .node {
  fill: #aaa;
}

.profile-activity-network .node circle {
  cursor: pointer;
  stroke-width: 2;
}

.profile-activity-network .node text {
  font: 11px helvetica;
  font-weight: 400;
  stroke: none;
  text-anchor: middle;
}

.profile-activity-network .node-connected circle {
  stroke: #999;
}

.profile-activity-network .node-connected text {
  fill: #666;
}

.profile-activity-network .node-unconnected text {
  fill: #bbb;
}

.profile-activity-network .node-unconnected circle {
  stroke: #ddd;
}

.profile-activity-network .node-looking-for-collaborators circle {
  stroke: #aff967;
}

.profile-activity-network .node-me circle {
  stroke: #008ee2;
}

.profile-activity-network-container {
  margin-bottom: 40px;
  position: relative;
}

.profile-activity-network-controls {
  margin-top: 15px;
}

.profile-activity-network-controls-label {
  font-size: 13px;
  font-weight: 300;
  padding-right: 15px;
}

.profile-activity-network-controls-outer {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
}

.profile-activity-network-controls-show-users {
  flex: 0 0 145px;
  margin-top: 15px;
  text-align: right;
}

.profile-activity-network-controls-title {
  font-size: 13px;
  font-weight: 600;
}

.profile-activity-network-preset {
  border: 0;
  padding: 0 2px;
  vertical-align: bottom;
}

.profile-activity-network-preset-disabled {
  color: #777;
  cursor: default;
}

.profile-activity-network-tooltip {
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 8px;
  color: #666;
  line-height: 1.4em;
  min-width: 200px;
  opacity: 1;
  position: absolute;
  text-align: center;
}

.profile-activity-network-tooltip::after {
  background: #fff;
  border: 1px solid #aaa;
  border-width: 0 1px 1px 0;
  bottom: -6px;
  content: '';
  display: block;
  height: 10px;
  position: absolute;
  transform: rotate(45deg);
  width: 10px;
  z-index: 1;
}

.profile-activity-network-tooltip-left::after {
  left: 24px;
}

.profile-activity-network-tooltip-right::after {
  right: 24px;
}

.profile-activity-network-tooltip-content {
  color: #aaa;
  font-size: 13px;
  margin-top: 10px;
  text-align: left;
}

.profile-activity-network-tooltip-header {
  background: #eee;
  border-bottom: 1px solid #ddd;
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 0;
  padding: 8px 10px;
  text-align: left;
}

.profile-activity-network-tooltip-inner {
  margin: 5px 10px;
}

.profile-activity-network-tooltip-profile-link {
  border: 0;
  display: block;
  font-size: 13px;
  padding: 0;
}

.profile-activity-network-tooltip-table {
  border-bottom: 1px solid #ddd;
  border-collapse: initial;
  font-size: 13px;
  margin: 10px 0;
  padding-bottom: 10px;
  width: 100%;
}

.profile-activity-network-tooltip-table-arrow {
  min-width: 18px;
  padding: 1px;
}

.profile-activity-network-tooltip-table-header {
  color: #aaa;
  font-weight: 300;
  padding: 1px;
}

.profile-activity-network-tooltip-table-interaction-type {
  padding: 1px 1px 1px 10px;
  text-align: left;
}

.profile-activity-network-tooltip-table-value {
  padding: 1px;
}

.profile-activity-network-tooltip-table-odd {
  background: #eee;
}
</style>