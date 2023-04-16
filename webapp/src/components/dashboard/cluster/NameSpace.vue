<template>
  <v-row>
    <v-col></v-col>
    <v-col>
      <v-text-field small dense single-line hide-details v-model="table.search" append-icon="mdi-magnify" label="搜索" ></v-text-field>
    </v-col>
    <v-col cols="2">
        <TableRefreshBtn :table="table" />
    </v-col>
    <v-col cols="12">
      <v-data-table dense :headers="table.headers" :loading="table.refreshing"  :items="table.items" item-key="name"
        :items-per-page="table.itemsPerPage" :search="table.search"
        show-select v-model="table.selected" show-expand single-expand>
        <template v-slot:[`item.creation`]="{ item }">
          {{ item.creation.timestamp }}
        </template>
        <template v-slot:[`item.labels`]="{ item }">
          <v-chip x-small label v-bind:key="key" v-for="value, key in item.labels" class="mr-2">{{ key}}={{value}}</v-chip>
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
      </v-data-table>
    </v-col>
    <DescribeResource :show.sync="showDescribeDialog" resource-name='namespace' :resource.sync="selectResource" />
  </v-row>
</template>

<script>

import { NamespaceTable } from '@/assets/app/tables';
import TableRefreshBtn from '../../plugins/TableRefreshBtn';
import DescribeResource from '../dialogs/DescribeResource.vue';

 export default {
    components: {
      TableRefreshBtn, DescribeResource,
    },
    data: () => ({
         table: new NamespaceTable(),
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
