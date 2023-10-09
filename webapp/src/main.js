import axios from 'axios';
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router';
import vuetify from './plugins/vuetify'

// import highlightPlugin from "@highlightjs/vue-plugin";
// import 'highlight.js/styles/dark.css';

import MESSAGE from './assets/app/message';

import App from './App.vue'
import ErrorPage from './ErrorPage.vue'

// cluster
import OverviewPage from './components/dashboard/cluster/OverviewPage'
import NodePage from './components/dashboard/cluster/NodePage';
import NameSpace from './components/dashboard/cluster/NameSpace';
// application -> workload
import WorkloadPage from './components/dashboard/application/WorkloadPage';
import DeploymentPage from './components/dashboard/application/workload/DeploymentPage';
import DaemonSet from './components/dashboard/application/workload/DaemonSet';
import CronJobPage from './components/dashboard/application/workload/CronJobPage';
import JobPage from './components/dashboard/application/workload/JobPage';
import StatefulSetPage from './components/dashboard/application/workload/StatefulSetPage';
// application -> pod
import PodPage from './components/dashboard/application/pod/PodPage';
// application -> config
import ServicePage from './components/dashboard/application/ServicePage';

// config
import ConfigMapPage from './components/dashboard/config/ConfigMapPage';
import SecretPage from './components/dashboard/config/SecretPage';

Vue.use(VueRouter)

Vue.config.productionTip = false
Vue.prototype.$MESSAGE = MESSAGE;

// Vue.use(highlightPlugin);

let router = new VueRouter({
    routes: [
        { path: '/overview', component: OverviewPage },
        { path: '/node', component: NodePage },
        { path: '/namespace', component: NameSpace },
        { path: '/workload', component: WorkloadPage,
         children: [
            {path: '/workload/deployment', component: DeploymentPage },
            {path: '/workload/daemonset', component: DaemonSet },
            {path: '/workload/statefulset', component: StatefulSetPage },
            {path: '/workload/cronjob', component: CronJobPage },
            {path: '/workload/job', component: JobPage },
         ]
        },
        { path: '/service', component: ServicePage },
        { path: '/pod', component: PodPage },
        { path: '/configmap', component: ConfigMapPage },
        { path: '/secret', component: SecretPage },
    ]
})

const CONFIG = 'config.json'

axios.get(CONFIG).then((resp) => {
    axios.defaults.baseURL = resp.data.backend_url;
    localStorage.static_stylesheet = JSON.stringify(resp.data.static_stylesheet);

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



