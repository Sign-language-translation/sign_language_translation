<!-- <template>
  <nav class="navbar">
    <ul class="nav-links">
      <li class="nav-item left">
        <router-link :to="{ name: 'VideoToText'}">
          Video to Text
        </router-link>
      </li>
      <li class="separator" />
      <li class="nav-item right">
        <router-link :to="{ name: 'TextToVideo'}">
          Text to Sign Video
        </router-link>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
/* Navbar Container */
.navbar {
  width: 100%;
  background-color: white;
  color: black;
  padding: 15px 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  height: 20px;
}

/* Flexbox for Centering */
.nav-links {
  width: 100%; /* Adjust to control spacing */
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  margin: 0;
  list-style: none;
}

/* Left and Right Sections */
.nav-item {
  flex: 1;
  text-align: center;
}

/* Separator in the middle */
.separator {
  width:1.031px;
  height: 38px;
  background-color: black;
}

.nav-links a {
  color: black;
  text-decoration: none;
  font-size: 1.2em;
  /* font-weight: bold; */
}

.nav-links a:hover {
  
  color: rgba(0, 0, 0, 0.6); /* Lighter shade of black */
  font-size: 1.23em; /* Slightly larger on hover */
  transition: color 0.3s ease-in-out, font-size 0.3s ease-in-out;
  
}

.router-link-active {
  font-weight: bold;
  text-decoration: underline; /* optional */
  color: #007BFF; /* optional highlight color */
}

/* Responsive: Adjust width on smaller screens */
@media (max-width: 768px) {
  .nav-links {
    width: 80%;
  }
}

@media (max-width: 480px) {
  .nav-links {
    width: 100%;
  }
}
</style> -->

<template>
  <nav class="navbar">
    <ul class="nav-links">
      <!-- Home Icon Section -->
      <li class="nav-item home">
        <router-link 
          :to="{ name: 'Main' }" 
          class="home-link"
        >
          <img
            src="@/assets/home.png"
            alt="Home"
            class="home-icon"
          >
        </router-link>
      </li>

      <!-- Center Section -->
      <li class="nav-item center">
        <router-link 
          :to="{ name: 'VideoToText' }"
        >
          Video to Text
        </router-link>
      </li>

      <li class="separator" />

      <li class="nav-item center">
        <router-link :to="{ name: 'TextToVideo' }">
          Text to Sign Video
        </router-link>
      </li>
    </ul>
  </nav>
</template>


<style scoped>
/* Navbar Container */
.navbar {
  width: 100%;
  background-color: white;
  color: black;
  padding: 15px 20px;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  height: 20px; /* Increase height for better spacing */
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Flex container for nav links */
.nav-links {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 2000px; /* Keep things centered and tidy */
  padding: 0;
  margin: 0;
  list-style: none;
}

/* Nav Items */
.nav-item {
  text-align: center;
}

.nav-item.home {
  margin-right: auto;
}

.nav-item.center {
  flex: 1;
  text-align: center;
}

.separator {
  width: 1px;
  height: 30px;
  background-color: rgba(0, 0, 0, 0.5);
  margin: 0 20px;
}

.nav-links a {
  color: rgba(0, 0, 0, 0.6);
  text-decoration: none;
  font-size: 1.2em;
}

.nav-links a:hover {
  color: rgba(0, 0, 0, 1);
  /* font-size: 1.23em; */
  transition: color 0.3s ease-in-out, font-size 0.3s ease-in-out;
}

.nav-links a.router-link-active {
  color: rgba(0, 0, 0, 1);
  transition: color 0.3s ease-in-out;
}
/* Home Icon styling */
.home-link {
  display: inline-block;
  transition: transform 0.3s ease-in-out;
}

/* .home-link:hover {
  transform: scale(1.2);
} */

.home-link .home-icon {
  filter: opacity(0.6);
}

.home-link:hover .home-icon {
  filter: opacity(1);
}

.home-icon {
  width: 25px;
  height: 25px;
  vertical-align: middle;
}

.router-link-active .home-icon {
  filter: opacity(1);
}

/* Responsive */
@media (max-width: 768px) {
  .nav-links {
    max-width: 100%;
  }
}

</style>
