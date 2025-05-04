<template>
  <div class="translation-result">
    <h2>Your Translation:</h2>
    <p>{{ result }}</p>
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
    }
  };
  </script>
  
  <style scoped>
  .translation-result {
    max-width: 600px;
    margin: 10px auto;
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
    font-size: 1.5em;
    color: black;
    margin-top: 40px;
  }
  
  .translation-result p {
    font-size: 1.2em;
    line-height: 1.5;
    color: #333;
    word-wrap: break-word;
    margin-top: -10px;
  }
  
  </style>
  