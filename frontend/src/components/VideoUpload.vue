<template>
  <div class="video-upload">
    <h2>Upload Your Sign Language Video</h2>
    <input 
      type="file"
      accept="video/*" 
      class="file-input"
      @change="onFileChange"
    >
    <button 
      :disabled="!videoFile" 
      @click="uploadVideo" 
    >
      Upload Video
    </button>
  </div>
</template>
  
  <script>
  export default {
    name: 'VideoUpload',
    emits: ['video-uploaded', 'reset-translation'],
    data() {
      return {
        videoFile: null,
      };
    },
    methods: {
      onFileChange(event) {
        this.videoFile = event.target.files[0];
        this.$emit('reset-translation'); // Emit event to reset the translation
      },
      async uploadVideo() {
        if (!this.videoFile) return;
  
        const formData = new FormData();
        formData.append('video', this.videoFile);
  
        try {
          // Replace with your backend API endpoint
        //   const response = await fetch('http://localhost:5000/api/translate', {
            const response = await fetch('http://localhost:3000/upload', {
            method: 'POST',
            body: formData,
          });
  
          const data = await response.json();
          this.$emit('video-uploaded', data.translation);  // Pass the result to App.vue
        } catch (error) {
          console.error('Error uploading video:', error);
        }
         }
    }
  };
  </script>
  
  <style scoped>
  .video-upload {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
    background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  }

  .file-input::file-selector-button{
    font-family: 'Montserrat', sans-serif;
  }

    
  .video-upload input {
    display: block;
    margin: 20px 0;
    padding: 10px;
    width: 96.5%;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-family: 'Montserrat', sans-serif;
  }

  @media (max-width: 600px) {
    .video-upload input {
        padding: 8px;
        font-size: 1em;
    }

    .video-upload button {
        font-size: 1em;
        padding: 10px;
    }
  }

  
  .video-upload button {
    width: 100%;
    padding: 12px;
    font-size: 1.1em;
    background-color: #ff6b6b; /* Use a vibrant color */
    color: white;
    border: none;
    padding: 10px 20px;
    /* font-size: 16px; */
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease, transform 0.2s ease;
  }

  .video-upload button:hover {
    background-color: #ff4a4a;
    transform: scale(1.02);
  }

  .video-upload button:disabled {
    background-color: #d3d3d3; /* Light gray to indicate disabled state */
    color: #a0a0a0; /* Dimmed text color for clarity */
    cursor: not-allowed;
    transform: none; /* Remove hover effects */
    box-shadow: none; /* Remove any shadow to make it look flat */
    opacity: 0.7; /* Slightly reduce opacity for a disabled effect */
  }

  </style>
  