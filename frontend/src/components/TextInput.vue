<template>
  <div class="text-input">
    <h2>Enter Text to Translate to Sign Language</h2>
  
    <input 
      v-model="inputText" 
      type="text" 
      placeholder="Type a sentence..." 
      class="text-field"
    >
  
    <button 
      :disabled="!inputText.trim() || isLoading" 
      @click="submitText"
    >
      Generate Video
    </button>
  
    <div 
      v-if="isLoading" 
      class="shimmer-wrapper"
    >
      <span class="shimmer-text">Generating video, please wait...</span>
    </div>
  
    <!-- Show submitted text after loading -->
    <div 
      v-if="submittedText && !isLoading" 
      class="submitted-text"
    >
      <h3>Your Input:</h3>
      <p>{{ submittedText }}</p>
    </div>
  </div>
</template>
  
  <script>
  export default {
    name: 'TextInput',
    props: {
    isLoading: Boolean,
    },
    emits: ['submit-text'],
    data() {
      return {
        inputText: '',
        submittedText: '',
      };
    },
    methods: {
      submitText() {
        this.submittedText = this.inputText.trim();
        this.inputText = '';
        // this.isLoading = true;
        this.$emit('submit-text', this.submittedText);
  
        // Simulate loading time (adjust to your real backend logic)
        // setTimeout(() => {
        //   this.isLoading = false;
        // }, 3000); // e.g., 3 seconds
      }
    }
  };
  </script>
  
  <style scoped>
  h2 {
    font-weight: 100;
  }
  
  .text-input {
    margin-bottom: 20px;
    align-items: center;
  }
  
  .text-field {
    width: 90%;
    max-width: 700px;
    padding: 12px;
    font-size: 1em;
    margin-bottom: 15px;
    border: 1px solid #ccc;
    border-radius: 6px;
    margin-right: 10px;
    font-family: 'Montserrat', sans-serif;
  }
  
  button {
    background-color: #ff6b6b;
    color: white;
    padding: 12px 24px;
    font-size: 1em;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: 0.3s ease;
    font-family: 'Montserrat', sans-serif;
  }
  
  button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  button:hover:enabled {
    background-color: #ff4a4a;
  }
  
  .shimmer-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 25px;
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

  
  .submitted-text {
    margin-top: 20px;
    padding: 15px;
    background-color: #f3f3f3; 
    border-radius: 6px; 
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); 
  }
  
  .submitted-text h3 {
    margin: 0 0 10px;
    font-size: 1.2em;
  }
  
  .submitted-text p {
    margin: 0;
    font-size: 1em;
    color: #333;
  }
  </style>
  