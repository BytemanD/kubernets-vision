import Vue from 'vue';
import Vuetify from 'vuetify/lib/framework';

import { VSnackbar, VBtn, VIcon } from "vuetify/lib";
import VuetifyToastPlugin from 'vuetify-toast-snackbar-ng';

Vue.use(Vuetify);

Vue.component("v-snackbar", VSnackbar);
Vue.component("v-btn", VBtn);
Vue.component("v-icon", VIcon);
// Vue.component("v-simple-table", VIcon);

Vue.use(VuetifyToastPlugin, {
    // 'x': 'center',
    timeout: 2000,
    showClose:  true,
    closeIcon: 'mdi-close',
    queueable: true,
});


export default new Vuetify({
});
