<template>
  <div class="video-upload">
    <h2>Upload Your Sign Language Video</h2>

    <!-- Input row: file input + mode selector -->
    <div class="input-row">
      <input 
        type="file"
        accept="video/*" 
        class="file-input"
        @change="onFileChange"
      >

      <div class="input-options">
        <select 
          id="mode"
          v-model="mode" 
          class="mode-select">
          <option value="sentence">
            Sentence
          </option>
          <option value="word">
            Word
          </option>
        </select>
      </div>
    </div>

    <!-- Video preview -->
    <div 
      v-if="videoPreview" 
      class="video-preview"
    >
      <video 
        :src="videoPreview" 
        controls 
        class="uploaded-video"
      />
    </div>

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
    emits: ['video-uploaded', 'reset-translation', 'start-translating'],
    data() {
      return {
        videoFile: null,
        videoPreview: null, // For storing video preview URL
        mode: 'sentence', // default
      };
    },
    methods: {
      onFileChange(event) {
        const file = event.target.files[0];
        if (file) {
        this.videoFile = file;
        this.videoPreview = URL.createObjectURL(file); // Generate a preview URL for the video
        this.$emit('reset-translation'); // Reset the translation result
        }
      },
      async uploadVideo() {
        if (!this.videoFile) return;

        this.$emit('start-translating'); // Emit event to show "Translating..."
  
        const formData = new FormData();
        formData.append('video', this.videoFile);
        formData.append('mode', this.mode); // Optional
  
        try {
          // Replace with your backend API endpoint
        //   const response = await fetch('http://localhost:5000/api/translate', {
            const response = await fetch('http://localhost:8888/upload', {
        // const response = await fetch('http://10.0.0.11:8888/upload', {

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
    /* width: 100%;  */
    max-width: 1000px;
    height: auto; 
    align-items: center;
    /* background-color: #fff;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); */
  }

  h2 {
    font-weight: 100;
  }

  .input-row {
  display: flex;
  align-items: center;
  gap: 15px; /* spacing between input and select */
  flex-wrap: wrap; /* makes it responsive */
  margin: 20px 0;
  }

  .file-input,
  .mode-select {
    padding: 10px;
    border-radius: 5px;
    border: 1px solid #ccc;
    font-family: 'Montserrat', sans-serif;
    font-size: 1rem;
    box-sizing: border-box;
    height: 42px;
  }
  
 .file-input {
  flex: 1;
  min-width: 200px;
  }


  .file-input::file-selector-button{
    font-family: 'Montserrat', sans-serif;
  }

  .input-options {
  display: flex;
  align-items: center;
  gap: 8px;
  }

  .mode-select {
  min-width: 150px;
  }

  .video-preview {
    margin-top: 20px;
    margin-left: 20px;
  }

 .uploaded-video {
  width: 100%;
  max-width: 500px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  }

  .video-upload input {
    display: block;
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
    margin-bottom: 30px;
  }

  .video-upload button:hover {
    background-color: #ff4a4a;
  }

  .video-upload button:disabled {
    /* background-color: #d3d3d3; 
    color: #a0a0a0; 
    cursor: not-allowed;
    transform: none;
    box-shadow: none; 
    opacity: 0.7;  */
    background-color: #ccc;
    cursor: not-allowed;
  }

  </style>
  