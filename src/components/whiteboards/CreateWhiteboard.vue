<template>
  <div>
    <BackToWhiteboards />
    <EditWhiteboard
      v-if="!isLoading"
      :on-cancel="cancel"
      :after-save="() => go('/whiteboards')"
    />
  </div>
</template>

<script>
import BackToWhiteboards from '@/components/util/BackToWhiteboards'
import Context from '@/mixins/Context'
import EditWhiteboard from '@/components/whiteboards/EditWhiteboard'
import Utils from '@/mixins/Utils'

export default {
  name: 'CreateWhiteboard',
  components: {BackToWhiteboards, EditWhiteboard},
  mixins: [Context, Utils],
  methods: {
    cancel() {
      this.$announcer.polite('Canceled')
      this.go('/whiteboards')
    }
  }
}
</script>
