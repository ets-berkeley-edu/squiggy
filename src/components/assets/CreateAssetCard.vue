<template>
  <v-card class="mb-3" no-gutters>
    <v-sheet class="fill-height">
      <v-container class="card-container fill-height px-5 text-center" fluid>
        <v-row>
          <v-col cols="18" sm="6">
            <v-btn
              block
              class="w-100"
              height="300"
              @click="go('/asset/upload')"
            >
              <div class="d-flex flex-column">
                <div class="pb-2">
                  <font-awesome-icon icon="laptop" size="lg" />
                </div>
                <div>
                  Upload
                </div>
              </div>
            </v-btn>
          </v-col>
          <v-col cols="18" sm="6">
            <v-btn
              block
              class="w-100"
              height="300"
              @click="go('/asset/create')"
            >
              <div class="d-flex flex-column">
                <div class="pb-2">
                  <font-awesome-icon icon="link" size="lg" />
                </div>
                <div>
                  Add Link
                </div>
              </div>
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>
  </v-card>
</template>

<script>
import Utils from '@/mixins/Utils'

export default {
  name: 'CreateAssetCard',
  mixins: [Utils]
}
</script>

<style scoped>
.card-container {
  min-width: 300px;
  align-content: center;
}
</style>