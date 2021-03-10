<template>
  <v-container fluid>
    <v-row>
      <v-col>
        AssetActivityTimeline
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'AssetActivityTimeline',
  props: {
    asset: {
      required: true,
      type: Object
    }
  }
}
</script>
