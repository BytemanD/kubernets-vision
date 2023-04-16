<template>
    <div>
        <v-btn-toggle mandatory dense rounded active-class='primary white--text'  class="mb-4 mt-0" v-model="toggleWorkloadIndex">
            <v-btn v-for="(item, i) in workLoadRouter" v-bind:key="item.name"
                @click="refreshRouter(i)">{{ i18n.t(item.name) }}</v-btn>
            <!-- <v-btn @click="routeTo('/workload/daemonset')">{{ i18n.t('daemonset') }}</v-btn>
            <v-btn @click="routeTo('/workload/statefulset')">{{i18n.t('statefulset')}}</v-btn>
            <v-btn @click="routeTo('/workload/cronjob')">{{i18n.t('cronjob')}}</v-btn>
            <v-btn @click="routeTo('/workload/job')">{{i18n.t('job')}}</v-btn> -->
        </v-btn-toggle>
        <router-view />
    </div>
</template>

<script>
import i18n from '@/assets/app/i18n';

const WORKLOAD_ROUTER = [
    {name: 'deployment', router: '/workload/deployment'},
    {name: 'daemonset', router: '/workload/daemonset'},
    {name: 'statefulset', router: '/workload/statefulset'},
    {name: 'cronjob', router: '/workload/cronjob'},
    {name: 'job', router: '/workload/job'},
]

export default {
    components: {

    },
    data: () => ({
        i18n: i18n,
        workLoadRouter: WORKLOAD_ROUTER,
        toggleWorkloadIndex: 0,
    }),
    methods: {
        refreshRouter(index) {
            let item = WORKLOAD_ROUTER[index];
            // console.log(this.$route.path, router, index)
            if (this.$route.path == item.router) {
                return;
            }
            this.$router.replace({ path: item.router })
        }

    },
    created: function () {
        this.refreshRouter(0)
    },
};
</script>
