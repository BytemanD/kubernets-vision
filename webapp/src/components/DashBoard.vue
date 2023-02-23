<template>
  <v-app>
    <v-navigation-drawer app permanent :expand-on-hover="miniVariant" :mini-variant="miniVariant" :dark="ui.dark">
      <v-list-item two-line class="px-2">
        <v-list-item-avatar class="ml-0" tile><img src="../../public/favicon.svg"></v-list-item-avatar>
        <v-list-item-content>
          <v-list-item-title>{{ name }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list shaped dense>
        <v-subheader><h3>资源</h3></v-subheader>
        <v-list-item-group v-model="navigation.item" color="primary">
          <v-list-item link active v-bind:key="i" v-for='(item, i) in navigation.items'>
            <v-list-item-icon><v-icon>{{ item.icon }}</v-icon></v-list-item-icon>
            <v-list-item-content>
              <v-list-item-title>{{ item.title }}</v-list-item-title>
            </v-list-item-content>
          </v-list-item>
        </v-list-item-group>
      </v-list>
      <!-- miniVariant -->
    </v-navigation-drawer>
    <v-app-bar app dense :dark="ui.dark">
      <v-app-bar-nav-icon @click="miniVariant = !miniVariant"></v-app-bar-nav-icon>
      <v-toolbar-title class="ml-1" style="width: 30%">
        <v-select solo-inverted flat hide-details :items="namespaceTable.items" prefix='命名空间:' class="rounded-0" item-text="name" v-model="namespace">
        </v-select>
      </v-toolbar-title>
      <v-spacer></v-spacer>
    </v-app-bar>
    <v-main>
      <v-container fluid>
        <v-row hidden>
          <v-col cols="12" :hidden="navigation.items[navigation.item].title != '节点'"><NodePage /></v-col>
          <v-col cols="12" :hidden="navigation.items[navigation.item].title != '命名空间'"><NameSpace /></v-col>
          <v-col cols="12" :hidden="navigation.items[navigation.item].title != '服务守护进程'"><DaemonSet :namespace.sync="namespace" /></v-col>
          <v-col cols="12" :hidden="navigation.items[navigation.item].title != 'Deployment'"><DeploymentPage :namespace.sync="namespace" /></v-col>
          <v-col cols="12" :hidden="navigation.items[navigation.item].title != 'Pod'"><PodPage :namespace.sync="namespace" /></v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { NamespaceTable } from '@/assets/app/tables';

import NodePage from './dashboard/NodePage';
import NameSpace from './dashboard/NameSpace';
import DaemonSet from './dashboard/DaemonSet';
import DeploymentPage from './dashboard/DeploymentPage';
import PodPage from './dashboard/PodPage';

// Edit v-container if edit navigationItems.
const navigationItems = [
  { title: '节点', icon: 'mdi-server', group: '资源' },
  { title: '命名空间', icon: 'mdi-alpha-n-circle', },
  { title: '服务守护进程', icon: 'mdi-alpha-s-circle' },
  { title: 'Deployment', icon: 'mdi-alpha-d-circle' },
  { title: 'Pod', icon: 'mdi-alpha-p-circle' },
]
export default {
  components: {
    NodePage, NameSpace, DaemonSet, DeploymentPage, PodPage
  },

  data: () => ({
    name: 'KubeVision',
    miniVariant: false,
    ui: {
      dark: true,
      navigationWidth: '200px'
    },
    navigation: {
      item: 0,
      items: navigationItems,
    },
    namespaceTable: new NamespaceTable(),
    namespace: 'default'
  }),
  methods: {

  },
  created() {
    this.namespaceTable.refresh();
  }
};
</script>
