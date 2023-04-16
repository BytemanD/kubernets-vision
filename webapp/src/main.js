import axios from 'axios';
import Vue from 'vue'
import VueI18n from 'vue-i18n'
import VueRouter from 'vue-router';
import vuetify from './plugins/vuetify'

import MESSAGE from './assets/app/message';

import App from './App.vue'
import ErrorPage from './ErrorPage.vue'

import OverviewPage from './components/dashboard/OverviewPage'
import NodePage from './components/dashboard/NodePage';
import NameSpace from './components/dashboard/NameSpace';
import WorkloadPage from './components/dashboard/WorkloadPage';
import PodPage from './components/dashboard/PodPage';
import ConfigMapPage from './components/dashboard/ConfigMapPage'
import ServicePage from './components/dashboard/application/ServicePage';

import DeploymentPage from './components/dashboard/workload/DeploymentPage';
import DaemonSet from './components/dashboard/workload/DaemonSet';
import CronJobPage from './components/dashboard/workload/CronJobPage';
import JobPage from './components/dashboard/workload/JobPage';
import StatefulSetPage from './components/dashboard/workload/StatefulSetPage';

Vue.use(VueRouter)

Vue.config.productionTip = false
Vue.prototype.$MESSAGE = MESSAGE;

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



