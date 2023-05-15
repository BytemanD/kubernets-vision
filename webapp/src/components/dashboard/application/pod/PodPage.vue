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
        <template v-slot:[`item.creation`]="{ item }">
          {{ item.creation && item.creation.timestamp }}
        </template>
        <template v-slot:[`item.ready`]="{ item }">
          {{ Utils.getPodReadyNum(item) }} /{{ item.container_statuses.length }}
        </template>
        <template v-slot:[`item.state`]="{ item }">
          {{ table.updateWaiting(item) }}
          <v-tooltip top v-if="table.waiting[item.name].reason">
            <template v-slot:activator="{ on, attrs }">
              <span class="warning--text" v-bind="attrs" v-on="on">{{ table.waiting[item.name].reason }}</span>
            </template>
            {{ table.waiting[item.name].message }}
          </v-tooltip>
          <v-tooltip top v-else-if="item.deletion && item.deletion.timestamp">
            <template v-slot:activator="{ on, attrs }">
              <span class="warning--text" v-bind="attrs" v-on="on">Terminating</span>
            </template>
            timestamp: {{ item.deletion.timestamp }} <br> grace_period_seconds: {{ item.deletion.grace_period_seconds }}
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
              <v-list-item @click="showPod(item)">
                <v-list-item-title>查看</v-list-item-title>
              </v-list-item>
              <v-list-item @click="describeResource(item)">
                <v-list-item-title>描述</v-list-item-title>
              </v-list-item>
              <v-list-item @click="openPodLogsDialog(item)">
                <v-list-item-title>日志</v-list-item-title>
              </v-list-item>
              <v-list-item @click="openPodExecDialog(item)">
                <v-list-item-title>执行命令</v-list-item-title>
              </v-list-item>
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
            <br>
          </td>
        </template>
      </v-data-table>
    </v-col>
    <DescribeResource :show.sync="showDescribeDialog" resource-name='pod' :resource="selectResource.name" />
    <PodLogs :show.sync="showPodLogsDialog" :pod="selectResource" />
    <PodExec :show.sync="showPodExecDialog" :pod="selectResource" />
    <PodDialog :show.sync="showPodDialog" :pod="selectResource" />
  </v-row>
</template>
<script>
import { Utils } from '@/assets/app/utils';
import { PodTable } from '@/assets/app/tables';

import TableRefreshBtn from '../../../plugins/TableRefreshBtn';
import DescribeResource from '../../dialogs/DescribeResource.vue';
import PodLogs from './dialogs/PodLogs.vue';
import PodExec from './dialogs/PodExec.vue';
import PodDialog from './dialogs/PodDialog.vue';

export default {
  components: {
    TableRefreshBtn, DescribeResource, PodLogs, PodExec,
    PodDialog,
  },
  data: () => ({
    Utils: Utils,
    table: new PodTable(),
    showDescribeDialog: false,
    selectResource: {},
    showPodLogsDialog: false,
    showPodExecDialog: false,
    showPodDialog: false,
  }),
  methods: {
    refresh: async function () {
      this.table.refresh();
    },
    describeResource: function (item) {
      this.selectResource = item;
      this.showDescribeDialog = !this.showDescribeDialog;
    },
    openPodLogsDialog: function (item) {
      this.selectResource = item;
      this.showPodLogsDialog = !this.showPodLogsDialog;
    },
    openPodExecDialog: function (item) {
      this.selectResource = item;
      this.showPodExecDialog = !this.showPodExecDialog;
    },
    showPod: function (item) {
      this.selectResource = item;
      this.showPodDialog = !this.showPodDialog;
    },
  },
  created: async function () {
    this.table.refresh();
  },
  watch: {

  }

};
</script>
 