<template>
  <v-app>
    <v-navigation-drawer app permanent :expand-on-hover="miniVariant" :mini-variant="miniVariant" width="200">
      <v-list-item two-line class="px-2">
        <v-list-item-avatar class="ml-0" tile><img src="../../public/favicon.svg"></v-list-item-avatar>
        <v-list-item-content>
          <v-list-item-title>{{ name }}</v-list-item-title>
        </v-list-item-content>
      </v-list-item>
      <v-list shaped dense>
        <v-list-item-group v-model="navigation.itemIndex" color="warning">
          <template v-for="group in navigation.group">
            <template>
              <v-subheader v-bind:key="group.name">
                <h3 class="primary--text">{{ i18n.t(group.name) }}</h3><v-divider></v-divider>
              </v-subheader>
              <v-list-item v-for="item in group.items" v-bind:key="item.router"
                :disabled="navigation.selectedItem.router == item.router" @click="selectItem(item)">
                <v-list-item-icon><v-icon>{{ item.icon }}</v-icon></v-list-item-icon>
                <v-list-item-content>
                  <v-list-item-title>{{ i18n.t(item.title) }}</v-list-item-title>
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
      <BtnNew />
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
import { Utils } from '@/assets/app/utils';
import { NamespaceTable } from '@/assets/app/tables';
import i18n from '@/assets/app/i18n';
import BtnTheme from './plugins/BtnTheme.vue';
import BtnAbout from './plugins/BtnAbout.vue';
import BtnNew from './plugins/BtnNew.vue';

const navigationGroup = [
  {
    name: 'cluster',
    items: [
      { title: 'overview', icon: 'mdi-alpha-o-circle', router: '/overview' },
      { title: 'namespace', icon: 'mdi-alpha-n-circle', router: '/namespace' },
      { title: 'node', icon: 'mdi-alpha-h-circle', router: '/node' },
    ]
  },
  {
    name: 'application',
    items: [
      { title: 'workload', icon: 'mdi-alpha-w-circle', router: '/workload' },
      { title: 'pod', icon: 'mdi-alpha-p-circle', router: '/pod' },
      { title: 'service', icon: 'mdi-alpha-s-circle', router: '/service' },
    ]
  },
  {
    name: 'configCenter',
    items: [
      { title: 'configMap', icon: 'mdi-alpha-c-circle', router: '/configmap' },
      { title: 'secret', icon: 'mdi-alpha-s-circle', router: '/secret' },
    ]
  },
]

export default {
  components: {
    BtnTheme, BtnAbout, BtnNew,
  },

  data: () => ({
    name: 'KubeVision',
    Utils: Utils,
    miniVariant: false,
    i18n: i18n,
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
          if (itemIndex != this.navigation.itemIndex){
            continue
          }
          this.selectItem(item)
          return;
        }
      }
    },
    selectItem(item) {
      Utils.setNavigationSelectedItem(item);
      this.navigation.selectedItem = item;
      if (this.$route.path != item.router){
        this.$router.replace({ path: item.router });
      }
    },
    setNamespace() {
      Utils.setNamespace(this.namespace);
      location.reload();
    },
    getItemIndexByRoutePath(routePath) {
      let itemIndex = -1;
      for (let groupIndex in this.navigation.group) {
        let group = this.navigation.group[groupIndex];
        for (let index in group.items) {
          let item = group.items[index];
          itemIndex += 1;
          if (routePath == item.router) {
            return itemIndex;
          }
        }
      }
    },
  },
  created() {
    this.namespace = Utils.getNamespace();
    let itemIndex = null;
    if (this.$route.path != '/') {
        itemIndex = this.getItemIndexByRoutePath(this.$route.path);
    } else {
      let localItem = Utils.getNavigationSelectedItem();
      if (localItem) {
        itemIndex = this.getItemIndexByRoutePath(localItem.router);
      }
    }
    if (itemIndex != null){
      this.navigation.itemIndex = itemIndex;
    }
    this.initItem();
    this.namespaceTable.refresh();
  }
};
</script>
