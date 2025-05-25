import { createRouter, createWebHistory } from 'vue-router';
import Main from "./pages/MainPage.vue";
import VideoToText from "./pages/VideoToText.vue";
import TextToVideo from "./pages/TextToVideo.vue";

const routes = [
    {
        path: "/",
        name: "Main",
        component: Main,
      },
      {
        path: "/video-to-text",
        name: "VideoToText",
        component: VideoToText,
      },
      {
        path: "/text-to-video",
        name: "TextToVideo",
        component: TextToVideo,
      },
      {
        path: '/:pathMatch(.*)*',
        name: 'NotFound',
        component: { template: '<h1>404 - Page Not Found</h1>' }
      },
      {
        path: '/test',
        name: 'Test',
        component: {
          template: '<div>Simple inline test</div>',
          mounted() {
            console.log("✅ Test route rendered");
          }
        }
      }
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
console.log("✅ Router setup complete:", routes);








// import { createRouter, createWebHistory } from 'vue-router';

// const routes = [
//   {
//     path: '/video-to-text',
//     name: 'VideoToText',
//     component: {
//       template: '<h2 style="color: red;">🚀 Router view is working!</h2>',
//       mounted() {
//         console.log("✅ Inline test component mounted");
//       }
//     }
//   }
// ];

// const router = createRouter({
//   history: createWebHistory(),
//   routes
// });

// export default router;