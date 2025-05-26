// import { createApp } from 'vue'
// import App from './App.vue'
// import router from './router';
// import './main.css';


// const app = createApp(App);
// app.use(router);
// app.mount('#app');
// console.log('router is', router);




// import { createApp } from 'vue';
// import App from './App.vue';
// import router from './router';

// console.log("router is", router);

// createApp(App)
//   .use(router)
//   .mount('#app');

// console.log("✅ App mounted");


import { createApp } from 'vue';
import App from './App.vue';
import router from './router';

const app = createApp(App);
app.use(router);
app.mount('#app');