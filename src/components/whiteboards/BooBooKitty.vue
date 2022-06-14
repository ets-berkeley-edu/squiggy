<template>
  <div>
    <div class="align-center d-flex flex-column mt-8 pt-10">
      <v-card
        v-if="!isLoading"
        class="elevation-1"
        outlined
      >
        <v-img
          alt="Laverne and Shirley with stuffed animals"
          aria-label="Laverne and Shirley with stuffed animals"
          width="300px"
          src="@/assets/boo-boo-kitty.jpg"
        />
        <v-card-text class="pt-5 text-center">
          <PageTitle :text="`Boo Boo ${kitty}`" />
          <div class="pb-3 pt-5">
            <v-text-field
              id="kitty-input"
              v-model="model"
              hide-details
              outlined
              required
              @keydown.enter="submit"
            />
          </div>
          <div>
            <v-btn
              id="submit-btn"
              text
              @click="submit"
              @keypress.enter="submit"
            >
              Submit
            </v-btn>
          </div>
        </v-card-text>
      </v-card>
    </div>
    <div class="sr-only">
      <v-main id="whiteboard-container" class="whiteboard-container">
        <!-- 'tabindex' is necessary in order to attach DOM element listener. -->
        <div id="whiteboard-viewport" class="whiteboard-viewport" tabindex="0">
          <canvas id="canvas"></canvas>
        </div>
      </v-main>
    </div>
  </div>
</template>

<script>
import Context from '@/mixins/Context'
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'
import Whiteboarding from '@/mixins/Whiteboarding'
import {getWhiteboard} from '@/api/whiteboards'

export default {
  name: 'BooBooKitty',
  components: {PageTitle},
  mixins: [Context, Utils, Whiteboarding],
  data: () => ({
    model: undefined
  }),
  created() {
    this.$loading()
    getWhiteboard(1).then(whiteboard => {
      this.init(whiteboard).then(whiteboard => {
        this.setDisableAll(false)
        this.$ready(whiteboard.title)
      })
    })
  },
  methods: {
    submit() {
      this.setKitty(this.model)
    }
  }
}
</script>
