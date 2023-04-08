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
      <v-data-table dense :headers="table.headers" :items="table.items" :loading="table.refreshing" item-key="name"
        :items-per-page="table.itemsPerPage" :search="table.search" show-select v-model="table.selected" show-expand
        single-expand>

        <template v-slot:[`item.ready`]="{ item }">
          {{ Utils.getPodReadyNum(item) }} /{{ item.container_statuses.length }}
        </template>
        <template v-slot:[`item.state`]="{ item }" >
          {{ table.updateWaiting(item) }}
          <v-tooltip top v-if="table.waiting[item.name].reason">
            <template v-slot:activator="{ on, attrs }">
              <span class="warning--text" v-bind="attrs" v-on="on">{{ table.waiting[item.name].reason }}</span>
            </template>
            {{ table.waiting[item.name].message }}
          </v-tooltip>
        </template>
        <template v-slot:[`item.containers`]="{ item }">
          <v-chip small label class="my-1 mr-1" v-for="container in item.containers" v-bind:key="container.name">
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
                    <v-list-item @click="describeResource(item)">
                        <v-list-item-title>描述</v-list-item-title>
                    </v-list-item>
                    <!-- <v-list-item @click="replaceResource(item)">
                        <v-list-item-title class="orange--text">替换</v-list-item-title>
                    </v-list-item> -->
                </v-list>
            </v-menu>
        </template>
        <template v-slot:expanded-item="{ headers, item }">
          <td></td>
          <td></td>
          <td :colspan="headers.length - 1">
            <table>
              <tr v-for="extendItem in table.extendItems" v-bind:key="extendItem.text">
                <td><strong>{{ extendItem.text }}:</strong> </td>
                <td>{{ item[extendItem.value] }}</td>
              </tr>
            </table>
          </td>
        </template>
      </v-data-table>
    </v-col>
    <DescribeResource :show.sync="showDescribeDialog" resource-name='pod' :resource.sync="selectResource" />
  </v-row>
</template>
<script>
import { Utils } from '@/assets/app/utils';
import { PodTable } from '@/assets/app/tables';

import TableRefreshBtn from '../plugins/TableRefreshBtn';
import DescribeResource from './dialogs/DescribeResource.vue';


export default {
  components: {
    TableRefreshBtn, DescribeResource,
  },
  data: () => ({
    Utils: Utils,
    table: new PodTable(),
    showDescribeDialog: false,
    selectResource: null,
  }),
  props: {
    namespace: String
  },
  methods: {
    refresh: async function () {
      this.table.refresh();
    },
    describeResource: function (item) {
        this.showDescribeDialog = !this.showDescribeDialog;
        this.selectResource = item.name;
    },
    // replaceResource: function (item) {
    //     this.showReplaceDialog = !this.showReplaceDialog;
    //     this.selectedItem = item;
    // }
  },
  created: async function () {
    this.table.refresh();
  },
  watch: {
    namespace(newValue) {
      this.table.namespace = newValue;
      this.table.refresh();
    }
  }

};
</script>
 