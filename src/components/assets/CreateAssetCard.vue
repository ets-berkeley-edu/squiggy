<template>
  <v-card class="mb-3" no-gutters>
    <v-sheet class="h-100">
      <v-container class="card-container fill-height text-center" fluid>
        <v-row no-gutters>
          <v-col class="column-left" cols="18" sm="6">
            <v-btn
              id="go-upload-asset-btn"
              block
              class="w-100"
              height="225"
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
          <v-col class="column-right" cols="18" sm="6">
            <v-btn
              id="go-add-link-asset-btn"
              block
              class="w-100"
              height="225"
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
        <v-row no-gutters>
          <v-col class="pt-2">
            <router-link
              aria-label="screenreaderText"
              class="hover-link"
              to="/bookmarklet/start"
            >
              Add assets from anywhere
            </router-link>
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
  align-content: center;
  padding: 0 6px 0 6px;
}
.column-left {
  padding: 0 7px 0 4px;
}
.column-right {
  padding: 0 4px 0 7px;
}
.hover-link {
  text-decoration: none;
}
.hover-link:hover {
  text-decoration: underline;
}
</style>
