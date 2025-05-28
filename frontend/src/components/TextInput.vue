<template>
  <div class="text-input">
    <h2>Enter Text to Translate to Sign Language</h2>
  
    <div class="input-row">
      <div class="input-wrapper">
        <input 
          v-model="inputText" 
          type="text" 
          placeholder="Type or speak..." 
          class="text-field"
        >
        <button 
          class="mic-btn" 
          :disabled="isLoading"
          :title="isRecording ? 'Stop recording' : 'Start recording'"
          @click="toggleRecording" 
        >
          <img 
            :src="microphoneIcon" 
            alt="Microphone" 
            class="mic-icon" 
            :class="{ recording: isRecording }" 
          >
        </button>
      </div>
    
      <button 
        class="generate-btn"
        :disabled="!inputText.trim() || isLoading" 
        @click="submitText"
      >
        Generate Video
      </button>
    </div>

  
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
  import microphoneIcon from '@/assets/microphone.png'

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
        isRecording: false,
        recognition: null,
        microphoneIcon,
      };
    },
    mounted() {
    // Initialize speech recognition (Hebrew)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      this.recognition = new SpeechRecognition();
      this.recognition.lang = 'he-IL';
      this.recognition.interimResults = false;
      this.recognition.maxAlternatives = 1;

      this.recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        this.inputText = transcript;
      };

      this.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        this.isRecording = false;
      };

      this.recognition.onend = () => {
        this.isRecording = false;
      };
    } else {
      alert('Speech Recognition is not supported in this browser.');
    }
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
      },
      toggleRecording() {
      if (!this.recognition) return;
      if (this.isRecording) {
        this.recognition.stop();
        this.isRecording = false;
      } else {
        this.recognition.start();
        this.isRecording = true;
      }
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
  
  /* .text-field {
    width: 90%;
    max-width: 700px;
    padding: 12px;
    font-size: 1em;
    margin-bottom: 15px;
    border: 1px solid #ccc;
    border-radius: 6px;
    margin-right: 10px;

    font-family: "Gisha", "Arial", "Helvetica", sans-serif;
  } */

  .input-row {
  display: flex;
  align-items: center;
  gap: 15px; /* space between input-wrapper and button */
  width: 100%;
  max-width: 1000px;
  margin-bottom: 15px;
  margin-left: 10px;
  
}
  .input-wrapper {
  position: relative;
  flex-grow: 1;
  width: 90%;
  max-width: 700px;
  margin-bottom: 15px;
  padding: 12px;
  margin-right: 50px;
}

.text-field {
  width: 100%;
  padding: 12px 40px 12px 12px; /* padding-right for icon space */
  font-size: 1em;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-family: "Gisha", "Arial", "Helvetica", sans-serif;
}

.mic-btn {
  position: absolute;
  right: -30px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

/* .mic-btn span.recording {
  color: red;
  animation: pulse 1s infinite;
} */

.mic-icon {
  width: 24px;
  height: 24px;
  filter: grayscale(100%);
  transition: filter 0.3s ease;
}

.mic-icon.recording {
  filter: none;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.4; }
  100% { opacity: 1; }
}

  
  .generate-btn {
    white-space: nowrap;
    background-color: #ff6b6b;
    color: white;
    padding: 12px 24px;
    font-size: 1em;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    transition: 0.3s ease;
    font-family: 'Montserrat', sans-serif;
    margin-bottom: 15px;
  }
  
  .generate-btn button:disabled {
    background-color: #ccc;
    cursor: not-allowed;
  }
  
  .generate-btn button:hover:enabled {
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
    font-family: "Gisha", "Arial", "Helvetica", sans-serif;
  }

  .record-btn {
  background-color: #6c63ff;
  color: white;
  padding: 12px 24px;
  font-size: 1em;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  margin-left: 10px;
  font-family: 'Montserrat', sans-serif;
}

.record-btn:hover:enabled {
  background-color: #4b44e0;
}
  </style>
  