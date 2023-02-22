import Vue from 'vue'
import App from './App.vue'
import vuetify from './plugins/vuetify'
import MESSAGE from './assets/app/message';

Vue.config.productionTip = false
Vue.prototype.$MESSAGE = MESSAGE;

new Vue({
  vuetify,
  render: h => h(App)
}).$mount('#app')
