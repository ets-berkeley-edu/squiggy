<template>
  <kinesis-container>
    <kinesis-element :strength="10" type="depth">
      <v-skeleton-loader
        v-if="whiteboard.isLoading"
        class="elevation-1 mx-auto"
        height="270"
        max-height="270"
        max-width="240"
        :tile="true"
        type="image, actions"
        width="240"
      />
      <v-card
        v-if="!whiteboard.isLoading"
        :id="`whiteboard-${whiteboard.id}`"
        hover
        class="card-class"
        @keypress.enter="go(`/whiteboard/${whiteboard.id}`)"
        @click="go(`/whiteboard/${whiteboard.id}`)"
      >
        <v-sheet elevation="1">
          <v-img
            aspect-ratio="1"
            class="thumbnail"
            :src="thumbnailUrl"
            @error="setImageError"
          >
            <v-card-text class="whiteboard-metadata">
              <div class="mb-3">
                {{ whiteboard.title }}
              </div>
              <div>
                by {{ oxfordJoin($_.map(whiteboard.users, 'canvasFullName')) }}
              </div>
            </v-card-text>
          </v-img>
        </v-sheet>
      </v-card>
    </kinesis-element>
  </kinesis-container>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'WhiteboardCard',
  mixins: [Utils],
  props: {
    whiteboard: {
      required: true,
      type: Object
    }
  },
  data: function() {
    return {
      imageError: false,
    }
  },
  computed: {
    thumbnailUrl: function () {
      if (!this.whiteboard.thumbnailUrl || this.imageError) {
        return require('@/assets/img-not-found.png')
      }
      return this.whiteboard.thumbnailUrl
    }
  },
  methods: {
    setImageError() {
      this.imageError = true
    }
  }
}
</script>

<style scoped>
.actions {
  padding: 6px 12px 4px 0;
}
.whiteboard-metadata {
  background-color: #333;
  background-color: rgba(51, 51, 51, 0.9);
  bottom: 0;
  color: #FFF;
  left: 0;
  position: absolute;
  right: 0;
}
.card-class {
  height: 100%;
}
.card-class:active, .card-class:focus {
  background-color: #378dc5;
}
.card-class:hover {
  background-color: #67bdf5;
}
</style>
