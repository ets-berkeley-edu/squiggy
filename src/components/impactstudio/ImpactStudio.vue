<template>
  <div id="impact-studio">
    <div class="mb-2 mt-2">
      <h2>Impact Studio</h2>
    </div>
    <SyncDisabled v-if="$currentUser.isAdmin || $currentUser.isTeaching" />
    <div v-if="!$currentUser.isAdmin && !$currentUser.isTeaching && ($currentUser.sharePoints === null)" id="impact-studio-splash" class="float-none">
      The Impact Studio is a studio for impact.
    </div>
  </div>
</template>

<script>
import SyncDisabled from '@/components/util/SyncDisabled'
import Utils from '@/mixins/Utils'

export default {
  name: 'ImpactStudio',
  mixins: [Utils],
  components: {SyncDisabled}
}
</script>
