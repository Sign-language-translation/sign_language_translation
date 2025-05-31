<template>
  <div class="video-result">
    <!-- <h2>Your Sign Language Video</h2> -->
    <video 
      :src="videoUrl" 
      controls 
      class="video-player"
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
    max-width: 700px;
    border-radius: 10px;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
  }
  </style>
  