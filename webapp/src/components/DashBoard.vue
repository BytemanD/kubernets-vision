<template>
    <v-app>
      <v-navigation-drawer app permanent :expand-on-hover="miniVariant" :mini-variant="miniVariant" dark>
          <v-list-item two-line class="px-2">
              <v-list-item-avatar class="ml-0" tile><img src="../../public/favicon.svg"></v-list-item-avatar>
              <v-list-item-content>
                <v-list-item-title>{{ name }}</v-list-item-title>
              </v-list-item-content>
          </v-list-item>
          <v-list shaped dense>
            <v-list-item-group v-model="navigation.item" color="primary">
                <template>
                    <!-- <v-subheader v-if="item.group"><h3>[[item.group]]</h3></v-subheader> -->
                    <v-list-item link active v-bind:key="i" v-for='(item, i) in navigation.items'>
                        <v-list-item-icon><v-icon>{{item.icon}}</v-icon></v-list-item-icon>
                        <v-list-item-content>
                            <v-list-item-title>{{item.title}}</v-list-item-title>
                        </v-list-item-content>
                    </v-list-item>
                </template>
            </v-list-item-group>
          </v-list>
           <!-- miniVariant -->
         </v-navigation-drawer>
         <v-app-bar app dark dense>
          <v-app-bar-nav-icon @click="toggleMiniVariant()"></v-app-bar-nav-icon>
            <!-- <div class="d-flex align-center">{{  miniVariant }}</div> -->
            <v-spacer></v-spacer>
          </v-app-bar>
      <v-main>
        <v-container fluid>
            <v-row hidden>
                <v-col cols="12" :hidden="navigation.items[navigation.item].title != '概览'"> <OverView /></v-col>
                <v-col cols="12" :hidden="navigation.items[navigation.item].title != '命名空间'"> <NameSpace /></v-col>
                <v-col cols="12" :hidden="navigation.items[navigation.item].title != '服务守护进程'"> <DaemonSet /></v-col>
                <v-col cols="12" :hidden="navigation.items[navigation.item].title != 'Deployment'"><DeploymentPage /></v-col>
                <v-col cols="12" :hidden="navigation.items[navigation.item].title != 'Pod'"><PodPage /></v-col>
            </v-row>
        </v-container>
      </v-main>
    </v-app>
</template>

<script>
import OverView from './dashboard/OverView';
import NameSpace from './dashboard/NameSpace';
import DaemonSet from './dashboard/DaemonSet';
import DeploymentPage from './dashboard/DeploymentPage';
import PodPage from './dashboard/PodPage';

const navigationItems = [
    { title: '概览', icon: 'mdi-view-dashboard' },
    { title: '命名空间', icon: 'mdi-alpha-n-circle', group: '资源' },
    { title: '服务守护进程', icon: 'mdi-alpha-s-circle' },
    { title: 'Deployment', icon: 'mdi-alpha-d-circle' },
    { title: 'Pod', icon: 'mdi-alpha-p-circle' },
]
  export default {
    components: {
        OverView, NameSpace, DaemonSet, DeploymentPage, PodPage
    },

    data: () => ({
        name: 'KubeVision',
        miniVariant: false,
        navigation: {
            item: 0,
            items: navigationItems,
        },

    }),
    methods: {
        toggleMiniVariant: function (){
            this.miniVariant = !this.miniVariant;
        },
    }
  };
</script>
