<template>
  <v-container v-if="isAuthorized && !isLoading" fluid>
    <v-row no-gutters>
      <v-col>
        <PageTitle text="Success!" />
        <div v-if="assetsCreated.length === 1" class="pt-3">
          Your new asset, named "{{ assetsCreated[0].title }}", has been added to
          the bCourses course site of <span id="asset-created-for-course" class="font-weight-bold">{{ course.name }}</span>.
        </div>
        <div v-if="assetsCreated.length > 1" class="pt-3">
          You created {{ assetsCreated.length }} assets, listed below. All were added to
          the bCourses course site of <span id="assets-created-for-course" class="font-weight-bold">{{ course.name }}</span>.
          <ul>
            <li v-for="(asset, index) in assetsCreated" :id="`asset-${index}`" :key="asset.id">
              <div :id="`asset-title-${index}`">{{ asset.title }}</div>
              <div v-if="asset.description" class="text--secondary">
                {{ asset.description }}
              </div>
            </li>
          </ul>
        </div>
      </v-col>
    </v-row>
    <v-row>
      <v-col class="pt-3">
        We are done. Click 'Close' button to exit.
      </v-col>
    </v-row>
    <v-row justify="end" no-gutters>
      <v-col class="pt-5">
        <BookmarkletButtons />
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import Bookmarklet from '@/mixins/Bookmarklet'
import BookmarkletButtons from '@/components/bookmarklet/BookmarkletButtons'
import Context from '@/mixins/Context'
import PageTitle from '@/components/util/PageTitle'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletPopup5',
  mixins: [Bookmarklet, Context, Utils],
  components: {BookmarkletButtons, PageTitle},
  created() {
    this.$ready('Bookmarklet success')
  }
}
</script>
