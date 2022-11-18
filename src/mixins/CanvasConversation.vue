<script>
export default {
  name: 'CanvasConversation',
  methods: {
    startCanvasConversation(user) {
      const url = (
        (this.$currentUser.useHttps ? 'https://' : 'http://') +
        this.$currentUser.canvasApiDomain +
        '/conversations?context_id=course_' +
        this.$currentUser.canvasCourseId +
        '&user_id=' +
        user.canvasUserId +
        '&user_name=' +
        encodeURIComponent(user.canvasFullName) +
        '#filter=type=inbox'
      )
      window.top.location.replace(url)
    }
  }
}
</script>
