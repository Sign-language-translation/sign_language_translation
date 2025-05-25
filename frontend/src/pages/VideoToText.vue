<template>
  <div class="content">
    <!-- <h1>Translate Sign Language Video to Text</h1> -->
    <video-upload 
      @video-uploaded="handleVideoUploaded"
      @reset-translation="resetTranslation" 
      @start-translating="startTranslating"
    />
    <div 
      v-if="isTranslating" 
      class="shimmer-wrapper"
    >
      <!-- <div 
      v-if="isTranslating" 
      class="translating-message"
    > -->
      <span class="shimmer-text">Translating...</span>
    </div>
    <!-- <div 
      ref="resultContainer" 
      class="result-container" 
      :class="{ 'show': showResult }"
    > -->
    <div 
      v-if="showResult" 
      class="result-container" 
    >
      <transition name="fade">
        <translation-result 
          v-if="showResult" 
          :result="result"
        />
      </transition>
    </div>
  </div>
</template>
  
<script>
import VideoUpload from '../components/VideoUpload.vue';
import TranslationResult from '../components/TranslationResult.vue';
  
export default {
    components: { VideoUpload, TranslationResult },
    data() {
      return {
        result: null,
        showResult: false,
        isTranslating: false
      };
    },
    mounted() {
    console.log("✅ VideoToText.vue mounted!");
    },
    methods: {
      handleVideoUploaded(result) {
        this.result = result;
        this.isTranslating = false;
        this.showResult = true;
      },
      resetTranslation() {
        this.result = null;
        this.showResult = false;
      },
      startTranslating() {
        this.isTranslating = true;
        this.showResult = false;
      }
    }
};
</script>
  

<style scoped>

/* Form Card (Content) */
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

.video-upload{
  align-items: center;
  padding-left: 30px;
  padding-right: 30px;
}


/* Heading Styles */
h1 {
  font-size: 2em;
  margin-top: -30px;
  font-weight: bold;
  /* text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);  */
  animation: fadeIn 1s ease-in-out; /* Animate heading fade-in */
}

h2 {
  font-size: 1em;
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

/* .result-container {
  overflow: hidden;
  max-height: 0;
  transition: max-height 0.6s ease-in-out;
}

.result-container.show {
  margin-bottom: -50px;
  max-height: 400px; 
} */


/* Fade transition for translation-result */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.6s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
}

.result-container{
  transition: max-height 0.6s ease-in-out;
  /* margin-bottom: 20px; */
}

/* Add styles for the "Translating..." message */
/* .translating-message {
  font-size: 1.2em;
  margin: 20px auto;
  color: #0056b3;
  margin-bottom: 20px;
  margin-top: 10px;
  animation: fadeIn 1s infinite alternate; 
} */

.shimmer-wrapper {
  display: flex;
  justify-content: center;
  margin: 10px auto;
  margin-bottom: 20px;
  /* margin-top: 25px; */
}

.shimmer-text {
  font-size: 1.2em;
  font-weight: 500;
  color: #606060;
  position: relative;
  overflow: hidden;
  display: inline-block;
}

/* THIS is the shimmer highlight that animates over the text */
.shimmer-text::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    120deg,
    transparent,
    rgba(255, 255, 255, 0.7),
    transparent
  );
  animation: shimmer-slide 2s infinite;
}

@keyframes shimmer-slide {
  0% {
    left: -100%;
  }
  100% {
    left: 100%;
  }
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


