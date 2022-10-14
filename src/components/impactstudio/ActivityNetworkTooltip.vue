<template>
  <div>
    <h4 class="profile-activity-network-tooltip-header">Activity Connections</h4>
    <div class="profile-activity-network-tooltip-inner">
      <table v-if="interactionCounts" class="profile-activity-network-tooltip-table">
        <tr>
          <th></th>
          <th class="profile-activity-network-tooltip-table-header text-right">
            {{ focalUser.id === $currentUser.id ? 'Me' : focalUser.canvasFullName.split(' ')[0] }}
          </th>
          <th></th>
          <th></th>
          <th class="profile-activity-network-tooltip-table-header text-left">
            {{ selectedUser.id === $currentUser.id ? 'Me' : selectedUser.canvasFullName }}
          </th>
        </tr>
        <tr v-for="(type, label) in interactionTypesEnabled" :key="label">
          <td class="profile-activity-network-tooltip-table-interaction-type">
            {{ label }}
          </td>
          <td class="profile-activity-network-tooltip-table-value text-right">
            {{ interactionCounts.left[label] }}
          </td>
          <td class="profile-activity-network-tooltip-table-arrow text-left">
            <i v-if="interactionCounts.left[label]" class="fa fa-long-arrow-right"></i>
          </td>
          <td class="profile-activity-network-tooltip-table-arrow text-right">
            <i v-if="interactionCounts.right[label]" class="fa fa-long-arrow-left"></i>
          </td>
          <td class="profile-activity-network-tooltip-table-value text-left">
            {{ interactionCounts.right[label] }}
          </td>
        </tr>
      </table>
      <div class="profile-activity-network-tooltip-content">
        <a class="profile-activity-network-tooltip-profile-link" :href="`/impact_studio/profile/${selectedUser.id}`">
          <div v-if="selectedUser.id === $currentUser.id && selectedUser.id !== user.id">
            View my profile
          </div>
          <div v-if="selectedUser.id !== $currentUser.id && selectedUser.id !== user.id">
            View {{ selectedUser.canvasFullName }}'s profile
          </div>
        </a>
        Last activity:
        <span v-if="selectedUser.lastActivity">{{ selectedUser.lastActivity | moment('from', 'now') }}</span>
        <span v-if="!selectedUser.lastActivity">Never</span>
      </div>
      <div v-if="selectedUser.lookingForCollaborators" class="profile-activity-network-tooltip-content">
        <v-btn
          id="tooltip-looking-for-collaborators-btn"
          color="success"
          @click="startCanvasConversation(selectedUser)"
          @keypress.enter.prevent="startCanvasConversation(selectedUser)"
        >
          <i class="pr-2 mdi mdi-account-plus"></i>
          Looking for Collaborators
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ActivityNetworkTooltip',
  props: {
    focalUser: {
      required: true,
      type: Object
    },
    interactionCounts: {
      required: false,
      type: Object,
      default: null
    },
    interactionTypesEnabled: {
      required: true,
      type: Object
    },
    selectedUser: {
      required: true,
      type: Object
    },
    startCanvasConversation: {
      required: true,
      type: Function
    },
    user: {
      required: true,
      type: Object
    }
  }
}
</script>

<style>
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
  border-spacing: 0;
  font-size: 13px;
  margin: 10px 0;
  padding-bottom: 10px;
  width: 100%;
}

.profile-activity-network-tooltip-table tr:nth-child(even) {
  background: #eee;
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
</style>
