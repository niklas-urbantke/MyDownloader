import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Schriften (offline, kein CDN)
import '@fontsource/montserrat/500.css'
import '@fontsource/montserrat/600.css'
import '@fontsource/montserrat/700.css'
import '@fontsource/open-sans/400.css'
import '@fontsource/open-sans/600.css'
import '@fontsource/open-sans/700.css'

// Batix-CI Design-System
import './design/colors_and_type.css'
import './design/batix-icons.css'
import './design/kit.css'

import App from './App.vue'
import { router } from './router'
import { i18n } from './i18n'

createApp(App).use(createPinia()).use(router).use(i18n).mount('#app')
