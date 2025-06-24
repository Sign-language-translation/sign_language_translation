<template>
  <div class="video-result">
    <!-- <h2>Your Sign Language Video</h2> -->
    <video
        ref="videoPlayer"
        :src="videoUrl"
        controls
        muted
        class="video-player"
        @loadeddata="handleVideoLoaded"
    />
  </div>
</template>
  
  <script>
  export default {
    name: 'VideoResult',
    props: {
      videoUrl: {
        type: String,
        required: true
      }
    },
    methods: {
      handleVideoLoaded() {
        this.$refs.videoPlayer.play().catch(e => {
          // Sometimes browsers block autoplay without user interaction.
          console.warn("Auto-play prevented:", e);
        });
      }
    }
  };
  </script>
  
  <style scoped>

  h2{
    font-size: 1.3em;
    font-weight: 100;

  }
  .video-result {
    margin-top: 10px;
  }
  
  .video-player {
    width: 100%;
    max-width: 500px;
    border-radius: 10px;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
  }
  </style>
  