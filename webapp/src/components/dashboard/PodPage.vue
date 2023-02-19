<template>
<v-data-table dense :headers="table.headers" :items="table.items" item-key="name"
  :items-per-page="table.itemsPerPage" :search="table.search"
  show-select v-model="table.selected" show-expand single-expand>

  <template v-slot:[`item.ready`]="{ item }">
    {{ item.ready_replicas }}/{{ item.replicas }}
  </template>

  <template v-slot:expanded-item="{ headers, item }">
    <td></td><td></td>
    <td :colspan="headers.length -1" >
      <table>
          <tr v-for="extendItem in table.extendItems" v-bind:key="extendItem.text">
            <td><strong>{{extendItem.text }}:</strong> </td><td>{{ item[extendItem.value] }}</td>
          </tr>
      </table>
    </td>
  </template>

</v-data-table>

</template>
<script>
import { PodTable } from '@/assets/app/tables';

export default {
     data: () => ({
        table: new PodTable(),
     }),
     created: async function () {
         this.table.refresh();
     },
 };
 </script>
 