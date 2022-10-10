import '@fortawesome/fontawesome-free/css/all.css'
import colors from 'vuetify/lib/util/colors'
import Vue from 'vue'
import Vuetify from 'vuetify/lib'
import {library} from '@fortawesome/fontawesome-svg-core'
import {faFontAwesome} from '@fortawesome/free-brands-svg-icons'
import {FontAwesomeIcon} from '@fortawesome/vue-fontawesome'
import {fas} from '@fortawesome/free-solid-svg-icons'
import {far} from '@fortawesome/free-regular-svg-icons'

// Find icons at https://fontawesome.com/icons
Vue.component('font-awesome-icon', FontAwesomeIcon) // eslint-disable-line vue/component-definition-name-casing
library.add(faFontAwesome)
library.add(far)
library.add(fas)

Vue.use(Vuetify)

export default new Vuetify( {
  icons: {
    iconfont: 'faSvg',
    values: {
      // See https://stackoverflow.com/questions/58712633/could-not-find-one-or-more-icons-warning-with-vuejs-application
      checkboxOff: {
        component: FontAwesomeIcon,
        props: {
          icon: ['far', 'square']
        }
      }
    }
  },
  theme: {
    themes: {
      light: {
        primary: '#378dc5',
        secondary: '#68acd8',
        accent: '#2a5f83',
        error: colors.red.accent3,
        'body-background': '#fff',
        'header-background': '#2a5f83',
        'icon-nav-dark-mode': '#2a5f83',
        'icon-nav-default': '#fff',
        'nav-background': '#378dc5',
        'table-border': '#979797'
      },
      dark: {
        primary: '#1B4663',
        secondary: '#2a5f83',
        accent: '#0d202c',
        error: colors.red.accent3,
        'body-background': '#0d202c',
        'header-background': '#122b3c',
        'icon-nav-dark-mode': '#2a5f83',
        'icon-nav-default': '#378dc5',
        'nav-background': '#173c55',
        'table-border': '#378dc5'
      }
    }
  }
})
