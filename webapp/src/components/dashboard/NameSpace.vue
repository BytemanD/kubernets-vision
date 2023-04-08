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
        <template v-slot:[`item.labels`]="{ item }">
          <v-chip x-small label v-bind:key="key" v-for="value, key in item.labels" class="mr-2">{{ key}}={{value}}</v-chip>
        </template>
      </v-data-table>
    </v-col>
  </v-row>
</template>

<script>

import { NamespaceTable } from '@/assets/app/tables';
import TableRefreshBtn from '../plugins/TableRefreshBtn';

 export default {
    components: {
      TableRefreshBtn
    },
    data: () => ({
         table: new NamespaceTable(),
     }),
    methods: {
       refresh: async function() {
          this.table.refresh();
       }
     },
    created: async function () {
         this.refresh();
     },
 };
</script>
