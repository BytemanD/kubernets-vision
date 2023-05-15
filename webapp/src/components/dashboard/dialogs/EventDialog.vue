<template>
  <v-row>
    <v-col class="my-auto">
      <v-icon color="warning">mdi-alert-circle</v-icon>警告
      <v-icon color="info" class="ml-4">mdi-information</v-icon> 正常
    </v-col>
    <v-col>
      <v-text-field single-line v-model="table.search" append-icon="mdi-magnify" label="搜索" ></v-text-field>
    </v-col>
    <v-col cols="2" class="my-auto">
        <TableRefreshBtn :table="table"/>
    </v-col>
    <v-col cols="12">
      <v-data-table dense :headers="table.headers" :loading="table.refreshing"  :items="table.items" item-key="name"
        :items-per-page="table.itemsPerPage" :search="table.search" v-model="table.selected">
        <template v-slot:[`item.involved_object`]="{ item }">
          {{ item.involved_object.kind }}/{{ item.involved_object.name }}
        </template>
        <template v-slot:[`item.type`]="{ item }">
          <v-icon color="warning" v-if="item.type.toLowerCase() == 'warning'">mdi-alert-circle</v-icon>
          <v-icon color="info" v-else-if="item.type.toLowerCase() == 'normal'">mdi-information</v-icon>
          <v-chip x-small v-else>{{ item.type }}</v-chip>
        </template>
        <template v-slot:[`item.message`]="{ item }">
          <v-tooltip top v-if="item.message.length > 0">
            <template v-slot:activator="{ on, attrs }">
              <span v-bind="attrs" v-on="on">{{ item.message.slice(0, 70) }} ...</span>
            </template>
            {{ item.message }}
          </v-tooltip>
          <span v-else>{{ item.message }}</span>
        </template>
      </v-data-table>
    </v-col>
    <DescribeResource :show.sync="showDescribeDialog" resource-name='namespace' :resource.sync="selectResource" />
  </v-row>
</template>

<script>

import { EventTable } from '@/assets/app/tables';
import TableRefreshBtn from '../../plugins/TableRefreshBtn';
import DescribeResource from '../dialogs/DescribeResource.vue';

 export default {
    components: {
      TableRefreshBtn, DescribeResource,
    },
    data: () => ({
         table: new EventTable(),
         showDescribeDialog: false,
         selectResource: null,
     }),
    methods: {
       refresh: async function() {
          this.table.refresh();
       },
       describeResource: function (item) {
        this.showDescribeDialog = !this.showDescribeDialog;
        this.selectResource = item.name;
    },
     },
    created: async function () {
         this.refresh();
     },
 };
</script>
