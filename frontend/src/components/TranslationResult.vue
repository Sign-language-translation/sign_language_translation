<template>
  <div class="translation-result">
    <h2>Your Translation:</h2>
    <p>{{ result }}</p>
    <img 
      src="@/assets/speaker.png" 
      alt="Listen" 
      class="speaker-icon" 
      :class="{ speaking: isSpeaking }"
      role="button" 
      tabindex="0"
      @click="speakText" 
      @keydown.enter="speakText" 
      @keydown.space.prevent="speakText"
    >
  </div>
</template>
  
<script>
export default {
  name: 'TranslationResult',
  props: {
    result: {
      type: String,
      required: true,
    }
  },
    data() {
    return {
      isSpeaking: false
    };
  },
  methods: {
    speakText() {
      if ('speechSynthesis' in window) {
        if (window.speechSynthesis.speaking) {
          // Stop any ongoing speech
          window.speechSynthesis.cancel();
          this.isSpeaking = false;
          return;
        }

        const utterance = new SpeechSynthesisUtterance(this.result);
        utterance.lang = 'he-IL';  // Hebrew (Israel)

        utterance.onstart = () => {
          this.isSpeaking = true;
        };

        utterance.onend = () => {
          this.isSpeaking = false;
        };

        utterance.onerror = () => {
          this.isSpeaking = false;
        };

        window.speechSynthesis.speak(utterance);
      } else {
        alert('Sorry, your browser does not support text to speech.');
      }
    }
  }
};
</script>
  
  <style scoped>
  .translation-result {
    max-width: 300px;
    margin: 10px auto;
  }

.speaker-icon {
  cursor: pointer;
  width: 28px;
  height: 28px;
  vertical-align: middle;
  margin-left: 8px;
  user-select: none;
  margin-top: -10px;
  margin-bottom: 10px;
  transition: filter 0.3s ease, scale 0.3s ease; /* smooth transition */
}

/* hover effect */
.speaker-icon:hover {
  scale: 1.1;
}

/* while speaking effect */
.speaker-icon.speaking {
  animation: pulse 1s infinite;
  filter: brightness(1.2);
  opacity: 1;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    filter: brightness(1.2);
  }
  50% {
    transform: scale(1.2);
    filter: brightness(1.4);
  }
  100% {
    transform: scale(1);
    filter: brightness(1.2);
  }
}

  @media (max-width: 600px) {
    .translation-result {
        padding: 15px;
    }

    .translation-result h2 {
        font-size: 1.5em;
    }

    .translation-result p {
        font-size: 1em;
    }
  }
  
  .translation-result h2 {
    font-size: 1.3em;
    color: black;
  }
  
  .translation-result p {
    font-size: 1.3em;
    line-height: 1.5;
    color: #333;
    word-wrap: break-word;
    margin-top: -5px;
    font-family: "Gisha", "Arial", "Helvetica", sans-serif;
  }
  
  </style>
  