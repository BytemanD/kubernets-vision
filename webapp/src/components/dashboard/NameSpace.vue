<template>
<v-data-table dense :headers="table.headers" :items="table.items" item-key="name"
  :items-per-page="table.itemsPerPage" :search="table.search"
  show-select v-model="table.selected" show-expand single-expand>

  <template v-slot:[`item.labels`]="{ item }">
    <v-chip x-small label v-bind:key="key" v-for="value, key in item.labels" class="mr-2">{{ key}}={{value}}</v-chip>
  </template>

</v-data-table>

</template>

<script>

import { NamespaceTable } from '@/assets/app/tables';

 export default {
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
