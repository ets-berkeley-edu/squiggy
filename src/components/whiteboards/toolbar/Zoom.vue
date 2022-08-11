<template>
  <v-btn-toggle class="ml-8 mr-3" rounded>
    <v-tooltip bottom color="primary">
      <template #activator="{on, attrs}">
        <v-btn
          id="zoom-in-btn"
          alt="Zoom in"
          color="teal lighten-3"
          dark
          fab
          small
          v-bind="attrs"
          v-on="on"
          @click="zoomIn"
        >
          <font-awesome-icon
            icon="plus"
            size="lg"
          />
        </v-btn>
      </template>
      <span>Zoom in</span>
    </v-tooltip>
    <v-tooltip bottom color="primary">
      <template #activator="{on, attrs}">
        <v-btn
          id="zoom-in-btn"
          alt="Zoom out"
          color="teal lighten-3"
          dark
          fab
          small
          v-bind="attrs"
          v-on="on"
          @click="zoomOut"
        >
          <font-awesome-icon
            icon="minus"
            size="lg"
          />
        </v-btn>
      </template>
      <span>Zoom out</span>
    </v-tooltip>
  </v-btn-toggle>
</template>

<script>
import Whiteboarding from '@/mixins/Whiteboarding'

export default {
  name: 'Zoom',
  mixins: [Whiteboarding]
}
</script>
