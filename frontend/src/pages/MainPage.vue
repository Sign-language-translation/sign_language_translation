<template>
  <div class="content">
    <h1>Welcome to Sign Language Translation</h1>
    <p>Translate sign language easily. Choose “Video to Text” to get fast transcripts of sign language videos or “Text to Sign Video” to see your words come to life.</p>
  </div>
</template>

<style scoped>
.content {
  margin: 40px auto;
  padding: 20px;
  background-color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
  width: 85%;
  max-width: 1000px;
  text-align: center;
  transition: all 0.3s ease-in-out;
  animation: slideIn 0.8s ease-in-out;
}

h1 {
  color: #222;
  font-size: 2.8em;
  margin-bottom: 0.5em;
}

p {
  color: #555;
  font-size: 1.2em;
  line-height: 1.6;
  margin-top: 0;
  margin-left: 2%;
  margin-right: 20px;
}


/* Animations */
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