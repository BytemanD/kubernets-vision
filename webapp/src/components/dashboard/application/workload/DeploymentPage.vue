<template>
  <v-row>
    <v-col>
      <v-btn small color="primary" class="mr-1"> <v-icon>mdi-plus</v-icon></v-btn>
      <v-btn small color="error" @click="table.deleteSelected()"> <v-icon>mdi-trash-can</v-icon></v-btn>
    </v-col>
    <v-col>
      <v-text-field small dense single-line hide-details v-model="table.search" append-icon="mdi-magnify"
        label="搜索"></v-text-field>
    </v-col>
    <v-col cols="2">
      <TableRefreshBtn :table="table" />
    </v-col>
    <v-col cols="12">
      <v-data-table dense :headers="table.headers" :loading="table.refreshing" :items="table.items" item-key="name"
        :items-per-page="table.itemsPerPage" :search="table.search" show-select v-model="table.selected" show-expand
        single-expand>
        <template v-slot:[`item.creation`]="{ item }">
          {{ item.creation.timestamp }}
        </template>
        <template v-slot:[`item.ready`]="{ item }">
          <span class="error--text" v-if="item.ready_replicas < item.replicas">
            {{ item.ready_replicas }}/{{ item.replicas }}
          </span>
          <span class="success--text" v-else>{{ item.ready_replicas }}/{{ item.replicas }}</span>
        </template>
        <template v-slot:[`item.containers`]="{ item }">
          <v-chip x-small label v-bind:key="container.name" v-for="container in item.containers" class="mr-1">
            {{ container.name }}
          </v-chip>
        </template>
        <template v-slot:[`item.actions`]="{ item }">
          <v-menu offset-y>
            <template v-slot:activator="{ on, attrs }">
              <v-btn icon color="purple" v-bind="attrs" v-on="on">
                <v-icon small>mdi-dots-vertical</v-icon></v-btn>
            </template>
            <v-list dense>
              <v-list-item @click="describeDeployment(item)">
                <v-list-item-title>描述</v-list-item-title>
              </v-list-item>
              <v-list-item @click="replaceDaemonSet(item)">
                <v-list-item-title class="orange--text">替换</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-menu>
        </template>
        <template v-slot:expanded-item="{ headers, item }">
          <td></td>
          <td :colspan="headers.length - 1">
            <table>
              <tr v-for="extendItem in table.extendItems" v-bind:key="extendItem.text">
                <td><strong>{{ extendItem.text }}:</strong> </td>
                <td>{{ item[extendItem.value] }}</td>
              </tr>
            </table>
            <v-simple-table dense class="grey lighten-2">
              <template v-slot:default>
                <thead>
                  <tr>
                    <th>容器</th>
                    <th>镜像</th>
                    <th>命令/参数</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="container in item.containers" v-bind:key="container.name">
                    <td>{{ container.name }}</td>
                    <td>{{ container.image }}</td>
                    <td>{{ Utils.getConainerCmd(container) }}</td>
                  </tr>
                </tbody>
              </template>
            </v-simple-table>
            <br>
            <v-simple-table dense class="grey lighten-2">
              <thead>
                <tr>
                  <th>初始化容器</th>
                  <th>镜像</th>
                  <th>命令/参数</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="container in item.init_containers" v-bind:key="container.name">
                  <td>{{ container.name }}</td>
                  <td>{{ container.image }}</td>
                  <td>{{ Utils.getConainerCmd(container) }}</td>
                </tr>
              </tbody>
            </v-simple-table>
          </td>
        </template>
      </v-data-table>
    </v-col>
    <DescribeResource :show.sync="showDescribeDialog" resource-name='deployment' :resource.sync="selectResource" />
  </v-row>
</template>
<script>
import { Utils } from '@/assets/app/utils';
import { DeploymentTable } from '@/assets/app/tables';

import TableRefreshBtn from '../../../plugins/TableRefreshBtn.vue';
import DescribeResource from '../../dialogs/DescribeResource.vue';

export default {
  components: {
    TableRefreshBtn, DescribeResource
  },
  props: {
    namespace: String
  },
  data: () => ({
    Utils: Utils,
    table: new DeploymentTable(),
    showDescribeDialog: false,
    selectResource: null
  }),
  methods: {
    refresh: async function () {
      this.table.refresh();
    },
    describeDeployment: function (item) {
      this.showDescribeDialog = !this.showDescribeDialog;
      this.selectResource = item.name;
    },
    replaceDaemonSet: function (item) {
      this.showReplaceDialog = !this.showReplaceDialog;
      this.selectedItem = item;
    }
  },
  created: async function () {
    this.refresh();
  },
  watch: {
    namespace(newValue) {
      this.table.namespace = newValue;
      this.table.refresh();
    }
  }
};
</script>
 