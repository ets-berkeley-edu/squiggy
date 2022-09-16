<script>
export default {
  name: 'CanvasConversation',
  methods: {
    startCanvasConversation(user) {
      const url = (
        (this.$_.get(this.$currentUser, 'course.canvas.useHttps') ? 'https://' : 'http://') +
        this.$_.get(this.$currentUser, 'course.canvasApiDomain') +
        '/conversations?context_id=course_' +
        this.$_.get(this.$currentUser, 'course.canvasCourseId') +
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
