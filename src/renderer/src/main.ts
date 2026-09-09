import { createApp } from 'vue'
import { createPinia } from 'pinia'

// Schriften (offline, kein CDN). urbDesign fragt "Segoe UI Variable" zuerst
// an und faellt dann auf Open Sans zurueck, deshalb wird nur diese gebraucht.
import '@fontsource/open-sans/400.css'
import '@fontsource/open-sans/600.css'
import '@fontsource/open-sans/700.css'

// urbDesign, Theme "Aero Plasma". Die Layer-Zeile muss vor den
// Stylesheets stehen, danach gilt: tokens < base < components < app.
import './design/layers.css'
import './design/tokens.css'
// Zweiter Token-Satz: der bisherige Batix-Look, waehlbar ueber data-style
import './design/classic.css'
import './design/components.css'
import './design/app.css'

import App from './App.vue'
import { router } from './router'
import { i18n } from './i18n'

createApp(App).use(createPinia()).use(router).use(i18n).mount('#app')
