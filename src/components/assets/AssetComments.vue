<template>
  <v-container fluid>
    <v-row>
      <v-col>
        AssetComments
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
export default {
  name: 'AssetComments',
  props: {
    asset: {
      required: true,
      type: Object
    }
  }
}
</script>
