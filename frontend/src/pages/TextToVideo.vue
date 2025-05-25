<template>
  <div class="content">
    <text-input 
      :is-loading="isLoading"
      @submit-text="handleSubmittedText" 
    />

    <video-result 
      v-if="!isLoading && resultVideoUrl" 
      :video-url="resultVideoUrl" 
    />

    <p 
      v-if="errorMessage" 
      class="error-message"
    >
      {{ errorMessage }}
    </p>
  </div>
</template>

<script>
import TextInput from '../components/TextInput.vue'
import VideoResult from '../components/VideoResult.vue'

export default {
  name: 'TextToVideo',
  components: {
    TextInput,
    VideoResult
  },
  data() {
    return {
      resultVideoUrl: null,
      isLoading: false, 
      errorMessage: null,
    }
  },
  methods: {
    async handleSubmittedText(text) {
      this.isLoading = true;

      try {
        this.errorMessage = null;
        this.resultVideoUrl = null;

        const response = await fetch('http://localhost:3000/generate_video', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ text: text })
        });

        const contentType = response.headers.get('content-type');
        const isJson = contentType && contentType.includes('application/json');
        const data = isJson ? await response.json() : null;

        if (!response.ok) {
          const errorMsg = data?.error || `Unexpected error (status ${response.status})`;
          throw new Error(errorMsg);
        }

        // const contentType = response.headers.get('content-type');
        // if (!contentType || !contentType.includes('application/json')) {
        //   throw new Error("Response is not JSON");
        // }


        // const data = await response.json();
        // console.log("✅ Backend response:", data);

        this.resultVideoUrl = data.video_url; // Assuming backend returns { video_url: "..." }

      } catch (error) {
        console.error("❌ Error fetching video:", error);
        this.resultVideoUrl = null;
        this.errorMessage = error.message;
      } finally {
        this.isLoading = false; // Set loading to false when done (either success or failure)
      }
    }
  },
}
</script>

<style>
.content {
  margin-top: 40px;
  margin-bottom: 40px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  width: 85%;
  max-width: 1000px;
  transition: all 0.3s ease-in-out;
  animation: slideIn 0.8s ease-in-out;
  align-items: center;
}

.video-result{
  margin-bottom: 20px;
}

.error-message {
  color: rgb(180, 0, 0);
  margin-top: 10px;
  text-align: center;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

</style>
