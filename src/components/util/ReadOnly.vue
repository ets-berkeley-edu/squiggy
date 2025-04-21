<template>
  <v-alert
    role="alert"
    outlined
    color="deep-orange darken-4"
    text
    type="info"
    elevation="2"
  >
    <div class="readonly-header">
      SuiteC tools are now read only.
    </div>
    <p class="readonly-content">
      All SuiteC tools (Asset Library, Engagement Index, Impact Studio and Whiteboards) are in a deprecated state. Assets, whiteboards, and activity data remain available for viewing but cannot be modified.
    </p>
  </v-alert>
</template>

<script>
export default {
  name: 'ReadOnly'
}
</script>

<style scoped>
.readonly-content {
  margin: 15px 0;
}
.readonly-header {
  font-weight: 600;
  margin: 0;
}
</style>
