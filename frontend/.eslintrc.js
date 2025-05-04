module.exports = {
    env: {
      node: true, // This will allow 'module' to be recognized
      browser: true, // If you're working with a browser-based project, add this too
    },
    extends: [
      'plugin:vue/vue3-recommended',
      'eslint:recommended',
    ],
    parserOptions: {
      parser: 'babel-eslint',
    },
    rules: {
      // Your custom ESLint rules
    },
  };