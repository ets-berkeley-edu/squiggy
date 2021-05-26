<template>
  <div id="points-configuration" class="points-configuration">
    <div class="mb-2 mt-2">
      <h2>Points Configuration</h2>
    </div>

    <div>
      <v-btn
        id="back-to-engagement-index-btn"
        class="bg-transparent"
        elevation="0"
        @click="go('/engage')"
        @keypress.enter="go('/engage')"
      >
        <font-awesome-icon class="mr-2" icon="less-than" size="sm" />
        Back to Engagement Index
      </v-btn>
    </div>

    <form
      class="points-container"
      name="activityTypeConfigurationForm"
      @submit="saveActivityTypeConfiguration"
    >
      <table id="enabled-activities-table" class="points-table" tabindex="-1">
        <thead>
          <tr>
            <th class="activity-title">Activity</th>
            <th class="text-center">Points</th>
            <th v-if="editMode" class="text-center">Action</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="activityType in enabledActivities" :key="activityType.type">
            <td class="activity-title">{{ activityType.title }}</td>
            <td v-if="!editMode" class="text-center">
              {{ activityType.points }}
            </td>
            <td v-if="editMode">
              <label :for="`points-edit-${activityType.type}`" class="sr-only">
                {{ activityType.title }}
              </label>
              <v-text-field
                :id="`points-edit-${activityType.type}`"
                v-model="activityType.points"
                class="points-edit"
                type="number"
                :outlined="true"
                hide-details
                required
              />
            </td>
            <td v-if="editMode" class="text-center">
              <v-btn
                :id="`disable-${activityType.type}`"
                type="button"
                @click.prevent="disableActivityType(activityType)"
                @keypress.enter.prevent="disableActivityType(activityType)"
              >
                Disable
              </v-btn>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="$currentUser.isAdmin || $currentUser.isTeaching">
        <div v-if="disabledActivities.length">
          <h3>Disabled Activities</h3>
          <table id="disabled-activities-table" class="points-table">
            <thead>
              <tr>
                <th class="activity-title">Activity</th>
                <th class="text-center">Points</th>
                <th v-if="editMode" class="text-center">Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="activityType in disabledActivities" :key="activityType.type">
                <td class="activity-title">{{ activityType.title }}</td>
                <td class="text-center">
                  {{ activityType.points }}
                </td>
                <td v-if="editMode" class="text-center">
                  <v-btn
                    :id="`enable-${activityType.type}`"
                    type="button"
                    @click.prevent="enableActivityType(activityType)"
                    @keypress.enter.prevent="enableActivityType(activityType)"
                  >
                    Enable
                  </v-btn>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="points-actions d-flex flex-row-reverse">
          <v-btn
            v-if="editMode"
            id="save-btn"
            type="submit"
            color="primary"
          >
            Save
          </v-btn>
          <v-btn
            v-if="!editMode"
            id="edit-btn"
            type="button"
            color="primary"
            @click.prevent="setEditMode(true)"
            @keypress.enter.prevent="setEditMode(true)"
          >
            Edit
          </v-btn>
          <v-btn
            v-if="editMode"
            id="cancel-edit-btn"
            class="mr-2"
            @click.prevent="setEditMode(false)"
            @keypress.enter.prevent="setEditMode(false)"
          >
            Cancel
          </v-btn>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import Utils from '@/mixins/Utils'
import {getPointsConfiguration, updatePointsConfiguration} from '@/api/activities'

export default {
  name: 'PointsConfiguration',
  mixins: [Utils],
  data: () => ({
    activities: [],
    editMode: false,
    originalActivities: [],
    pointsConfiguration: null
  }),
  computed: {
    disabledActivities() {
      return this.activities.filter(a => !a.enabled)
    },
    enabledActivities() {
      return this.activities.filter(a => a.enabled)
    }
  },
  methods: {
    disableActivityType(activityType) {
      activityType.enabled = false
      this.$announcer.polite(`Disabled activity: ${activityType.title}`)
    },
    enableActivityType(activityType) {
      activityType.enabled = true
      this.$announcer.polite(`Enabled activity: ${activityType.title}`)
    },
    saveActivityTypeConfiguration() {
      updatePointsConfiguration(this.activities).then(() => {
        this.editMode = false
        this.$announcer.polite('Saved points configuration')
      })
    },
    setEditMode(mode) {
      this.editMode = mode
      if (this.editMode) {
        this.originalActivities = this.activities.map((a) => { return {...a}})
      } else {
        this.activities = this.originalActivities
      }
      this.$announcer.polite(mode ? 'Editing points configuration' : 'Canceled points configuration edit')
      this.$putFocusNextTick('enabled-activities-table')
    }
  },
  created() {
    this.$loading()
    getPointsConfiguration().then((data) => {
      this.activities = data
      this.$ready('Points configuration')
    })
  }
}
</script>

<style scoped>
.activity-title {
  text-align: left;
}
.points-container {
  width: 600px;
}
.points-edit {
  width: 60px;
}
.points-table {
  border: 1px solid #ccc;
  border-collapse: collapse;
  margin: 20px 0 30px 0;
  width: 100%;
}
.points-table tbody tr:nth-of-type(even) {
  background-color: rgba(0, 0, 0, .03);
}
.points-table thead {
  border: 1px solid #ccc;
}
.points-table thead th {
  background-color: rgba(0, 0, 0, .03);
  border: none;
  color: #000 !important;
  font-size: 14px;
  padding: 15px;
}
.points-table tbody td {
  border: none;
  font-size: 14px !important;
  padding: 15px;
}
</style>

<style>
.v-input__slot {
  min-height: 35px !important;
}
</style>