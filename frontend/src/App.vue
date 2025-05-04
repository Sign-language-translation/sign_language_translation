<template>
  <div id="app">
    <div class="content">
      <h1>Sign Language Video Translator</h1>
      <video-upload 
        @video-uploaded="handleVideoUploaded"
        @reset-translation="resetTranslation" 
      />
      <div 
        class="result-container" 
        :class="{ 'show': showResult }"
        ref="resultContainer"
      >
        <transition name="fade">
          <translation-result 
            v-if="showResult" 
            :result="result"
          />
        </transition>
      </div>
    </div>
  </div>
</template>

<script>
import VideoUpload from './components/VideoUpload.vue';
import TranslationResult from './components/TranslationResult.vue';

export default {
  name: 'App',
  components: {
    VideoUpload,
    TranslationResult
  },
  data() {
    return {
      result: null,
      showResult: false, // Control visibility of the translation result
    };
  },
  methods: {
    handleVideoUploaded(result) {
      this.result = result;
      this.showResult = true;
    },
    resetTranslation() {
      this.result = null; // Clear the translation result
      this.showResult = false; // Hide the result component
    }
  }
};
</script>

<style scoped>

#app {
  text-align: center;
  font-family: 'Montserrat', sans-serif;
  color: #333;
  position: relative; /* Required for pseudo-element positioning */
  height: 100vh;
  margin: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
}

/* Add a dark overlay with blur */
#app::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: 
    linear-gradient(rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.1)),
    url('@/assets/sign1.jpg') left center no-repeat, 
    url('@/assets/sign2.jpg') center center no-repeat, 
    url('@/assets/sign3.jpg') right center no-repeat;
  background-size: 33.33vw 100vh;
  filter: blur(2px); /* Apply blur to the background images */
  z-index: -1; /* Ensure it stays behind the content */
}

.video-upload{
  margin-top: 40px;
}

/* Heading Styles */
h1 {
  font-size: 2.8em;
  margin-top: -30px;
  /* text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);  */
  animation: fadeIn 1s ease-in-out; /* Animate heading fade-in */
}

h2 {
  font-size: 1.8em;
  color: #007BFF;
  margin-bottom: 10px;
}

/* Button Styles */
button {
  background-color: #007BFF;
  color: white;
  font-size: 1em;
  padding: 10px 20px;
  border: none;
  cursor: pointer;
  border-radius: 5px;
  transition: background-color 0.3s ease, transform 0.2s ease;;
}

button:hover {
  background-color: #0056b3;
  transform: scale(1.05); /* Add slight zoom effect on hover */
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}


/* Form Card (Content) */
.content {
  background-color: rgba(255, 255, 255, 0.8); /* White background with 70% transparency */
  border-radius: 8px;
  padding: 85px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
  width: 70%; /* Adjust width as needed */
  height: auto; 
  max-width: 2000px; /* Ensure it's not too wide */
  max-height: 60vh; /* Maximum height is 80% of the viewport height */
  min-height: 280px; /* Minimum height for smaller screens */
  transition: height 0.3s ease-in-out; /* Smooth height transition */
  margin: 20px auto; /* Center content and add spacing around it */
  animation: slideIn 0.8s ease-in-out; /* Animate form sliding in */
}

.result-container {
  overflow: hidden;
  max-height: 0;
  transition: max-height 0.6s ease-in-out;
}

.result-container.show {
  max-height: 500px; /* Set this to a value larger than the maximum expected height */
}


/* Fade transition for translation-result */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.6s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
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
