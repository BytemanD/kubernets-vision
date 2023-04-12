import axios from 'axios';
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router';
import vuetify from './plugins/vuetify'

import MESSAGE from './assets/app/message';

import App from './App.vue'
import ErrorPage from './ErrorPage.vue'

import NodePage from './components/dashboard/NodePage';
import NameSpace from './components/dashboard/NameSpace';
import DaemonSet from './components/dashboard/DaemonSet';
import DeploymentPage from './components/dashboard/DeploymentPage';
import PodPage from './components/dashboard/PodPage';
import ConfigMapPage from './components/dashboard/ConfigMapPage'
import OverviewPage from './components/dashboard/OverviewPage'


Vue.use(VueRouter)

Vue.config.productionTip = false
Vue.prototype.$MESSAGE = MESSAGE;

let router = new VueRouter({
    routes: [
        { path: '/node', component: NodePage },
        { path: '/namespace', component: NameSpace },
        { path: '/daemonset', component: DaemonSet },
        { path: '/deployment', component: DeploymentPage },
        { path: '/pod', component: PodPage },
        { path: '/configmap', component: ConfigMapPage },
        { path: '/overview', component: OverviewPage },
    ]
})

const CONFIG = 'config.json'

axios.get(CONFIG).then((resp) => {
    axios.defaults.baseURL = resp.data.backend_url;

    new Vue({
      vuetify,
      VueI18n,
      router,
      render: h => h(App)
    }).$mount('#app')

}).catch((error) => {
    let propsData = {
        title: `无法获取服务配置 ${CONFIG}`,
        error: error,
    };
    new Vue({
        vuetify,
        VueI18n,
        render: h => h(ErrorPage, {props: propsData}),
    }).$mount('#app')
});



