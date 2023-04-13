<template>
  <v-app>
    <v-navigation-drawer app permanent :expand-on-hover="miniVariant" :mini-variant="miniVariant"
      width="200">
      <v-list-item two-line class="px-2">
        <v-list-item-avatar class="ml-0" tile><img src="../../public/favicon.svg"></v-list-item-avatar>
        <v-list-item-content>
          <v-list-item-title>{{ name }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list shaped dense>
        <v-list-item-group v-model="navigation.itemIndex" color="primary">
          <template v-for="group in navigation.group">
            <template>
              <v-subheader v-bind:key="group.name">
                <h3 class="primary--text">{{ group.name }}</h3><v-divider></v-divider>
              </v-subheader>
              <v-list-item v-for="item in group.items" v-bind:key="item.router"
                :disabled="navigation.selectedItem.router == item.router" @click="selectItem(item)">
                <v-list-item-icon><v-icon>{{ item.icon }}</v-icon></v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ item.title }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
          </template>
        </v-list-item-group>
      </v-list>
    </v-navigation-drawer>
    <v-app-bar app dense>
      <v-app-bar-nav-icon @click="miniVariant = !miniVariant"></v-app-bar-nav-icon>
      <v-toolbar-title class="ml-1" style="width: 300px">
        <v-select solo-inverted flat hide-details :items="namespaceTable.items" prefix='命名空间:' class="rounded-0"
          item-text="name" v-model="namespace" v-on:change="setNamespace()">
        </v-select>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <BtnTheme />
      <BtnAbout />
    </v-app-bar>
    <v-main>
      <v-container fluid>
        <router-view></router-view>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import { NamespaceTable } from '@/assets/app/tables';
import BtnTheme from './plugins/BtnTheme.vue';
import BtnAbout from './plugins/BtnAbout.vue';
import { Utils } from '@/assets/app/utils';

const navigationGroup = [
  {
    name: '集群',
    items: [
      { title: '概览', icon: 'mdi-alpha-o-circle', router: '/overview' },
      { title: '命名空间', icon: 'mdi-alpha-n-circle', router: '/namespace' },
      { title: '节点', icon: 'mdi-alpha-h-circle', router: '/node' },
    ]
  },
  {
    name: '负载',
    items: [
      { title: 'DaemonSet', icon: 'mdi-alpha-s-circle', router: '/daemonset' },
      { title: 'Deployment', icon: 'mdi-alpha-d-circle', router: '/deployment' },
      { title: 'Pod', icon: 'mdi-alpha-p-circle', router: '/pod' },
      { title: 'ConfigMap', icon: 'mdi-alpha-c-circle', router: '/configmap' },
    ]
  },
]

export default {
  components: {
    BtnTheme, BtnAbout
  },

  data: () => ({
    name: 'KubeVision',
    miniVariant: false,
    ui: {
      navigationWidth: '200px'
    },
    navigation: {
      itemIndex: 0,
      selectedItem: {},
      group: navigationGroup,
    },
    namespaceTable: new NamespaceTable(),
    namespace: 'default'
  }),
  methods: {
    initItem() {
      let itemIndex = -1;
      for (let groupIndex in this.navigation.group) {
        let group = this.navigation.group[groupIndex];
        for (let itemIndx in group.items) {
          let item = group.items[itemIndx];
          itemIndex += 1;
          if (this.$route.path != item.router) { continue }
          this.selectItem(item);
          this.navigation.itemIndex = itemIndex;
          return;
        }
      }
    },
    selectItem(item) {
      localStorage.setItem('navigationSelectedItem', JSON.stringify(item));
      this.navigation.selectedItem = item;
      if (this.$route.path == '/' || this.$route.path != item.router) {
        this.$router.replace({ path: item.router });
      }
    },
    setNamespace(){
      Utils.setNamespace(this.namespace);
      location.reload();
    }
  },
  created() {
    this.namespace = Utils.getNamespace();
    if (this.$route.path == '/') {
      let localItem = localStorage.getItem('navigationSelectedItem');
      if (localItem) {
        this.selectItem(JSON.parse(localItem));
      } else {
        this.selectItem(navigationGroup[0].items[0]);
      }
    } else {
      this.initItem();
    }
    this.namespaceTable.refresh();
  }
};
</script>
