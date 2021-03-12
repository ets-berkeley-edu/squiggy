<template>
  <div v-if="!isLoading" class="align-center d-flex flex-column mt-10">
    <h1 class="grey--text text--darken-2">Squiggy says HELLO</h1>
    <div class="align-center d-flex flex-column justify-space-between mb-4">
      <v-slider
        v-model="width"
        class="align-self-stretch"
        min="200"
        max="500"
        step="1"
      />
      <v-img
        :aspect-ratio="16 / 9"
        :width="width"
        src="@/assets/hello.jpg"
      />
    </div>
    <div v-if="$currentUser.isAuthenticated">
      <CourseSummaryCard :course="$currentUser.course" />
    </div>
    <div v-if="!$currentUser.isAuthenticated">
      <DevAuth :canvas-domains="canvasDomains" />
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import CourseSummaryCard from '@/components/course/CourseSummaryCard'
import DevAuth from '@/components/util/DevAuth'
import Utils from '@/mixins/Utils'
import {getAllCanvasDomains} from '@/api/courses'

export default {
  name: 'Squiggy',
  components: {CourseSummaryCard, DevAuth},
  mixins: [Context, Utils],
  data: () => ({
    canvasDomains: undefined,
    width: 300
  }),
  created() {
    this.$loading()
    getAllCanvasDomains().then(data => {
      this.canvasDomains = data
      this.$ready()
    })
  }
}
</script>
