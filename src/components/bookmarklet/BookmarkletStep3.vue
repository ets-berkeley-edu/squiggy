<template>
  <div>
    <BackToAssetLibrary anchor="asset-library" :disabled="isLoading" />
    <div class="align-center d-flex">
      <div class="pr-3">
        <font-awesome-icon icon="bookmark" size="lg" />
      </div>
      <div>
        <h2>{{ pageTitle }}</h2>
      </div>
    </div>
    <div v-if="!isLoading" class="pt-2 w-100">
      <img
        :aria-label="`Screenshot showing ${pageTitle}`"
        :alt="`Screenshot showing ${pageTitle}`"
        :src="screenshot"
      />
      <div>
        <!--
        Drag <a class="btn btn-default assetlibrary-addbookmarklet-bookmarklet" data-ng-click="preventBookmarklet($event)" data-ng-mousedown="trackBookmarkInstallation()" data-ng-href="javascript:
            (function() {
              var api_domain = '{{ null // me.course.canvas_api_domain }}';
              var base_url = '{{ null // baseUrl }}';
              var bookmarklet_token = '{{ null //  me.bookmarklet_token }}';
              var course_id = '{{ null //  me.course.canvas_course_id }}';
              var tool_url = '{{ null // toolUrl }}';
              var user_id = '{{ null // me.id }}';
              window.collabosphere = window.collabosphere || {
                'initialized': false,
                'api_domain': api_domain,
                'base_url': base_url,
                'bookmarklet_token': bookmarklet_token,
                'course_id': course_id,
                'tool_url': tool_url,
                'user_id': user_id
              };
              if (window.collabosphere.initialized) {
                var iframe = document.getElementById('collabosphere-iframe');
                if (iframe) {
                  iframe.contentWindow.postMessage('collabosphere.load', '*');
                }
              } else {
                window.collabosphere.initialized = true;
                var bookmarklet = document.createElement('script');
                bookmarklet.src = base_url + '/assets/js/bookmarklet-init.js';
                document.body.appendChild(bookmarklet);
              }
            })();"><i class="fa fa-bookmark"></i> Asset Library</a> to the browser's <span data-ng-bind="toolbar"></span>.
          -->
      </div>
      <div class="float-right">
        <v-btn
          id="go-to-next-step-btn"
          class="bg-transparent pl-0"
          elevation="0"
          @click="go('/bookmarklet/step4')"
          @keypress.enter="go('/bookmarklet/step4')"
        >
          Next
          <font-awesome-icon class="ml-2" icon="greater-than" size="lg" />
        </v-btn>
      </div>
    </div>
  </div>
</template>

<script>
import BackToAssetLibrary from '@/components/util/BackToAssetLibrary'
import Context from '@/mixins/Context'
import Utils from '@/mixins/Utils'

export default {
  name: 'BookmarkletStart',
  components: {BackToAssetLibrary},
  mixins: [Context, Utils],
  data: () => ({
    pageTitle: 'How to enable the bookmark',
    screenshot: undefined
  }),
  created() {
    this.screenshot = require(`@/assets/bookmarklet/bookmarklet-3-${this.currentBrowser}.png`)
    this.$ready(this.pageTitle)
  }
}
</script>
