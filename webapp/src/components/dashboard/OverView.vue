<template>
   <div>
        <h2>节点</h2>
        <v-btn fab x-small color="info" v-on:click="table.refresh()" >
            <v-icon v-if="table.refreshing" class="mdi-spin">mdi-rotate-right</v-icon>
            <v-icon v-else>mdi-rotate-right</v-icon>
        </v-btn>
        <v-data-table dense :headers="table.headers" :items="table.items" item-key="name"
            :items-per-page="table.itemsPerPage" :search="table.search"
            show-select v-model="table.selected" show-expand single-expand>

            <template v-slot:[`item.name`]="{ item }">
                <v-chip small label class="info"> {{ item.name }}</v-chip>
            </template>
            
            <template v-slot:[`item.os_image`]="{ item }">
                <v-chip x-small label>{{ item.os_image }}</v-chip>
            </template>

            <template v-slot:[`item.labels`]="{ item }">
                <template v-for="value, key in item.labels">
                    <v-chip x-small label close v-if="table.hideLabels.indexOf(key) < 0" v-bind:key="key"
                     class="mr-2" @click:close="table.deleteLabel(item, key)">{{key}}={{value}}</v-chip>
                </template>
            </template>

            <template v-slot:[`expanded-item`]="{ headers, item }">
                <td></td><td></td>
                <td :colspan="headers.length -1" >
                    <table>
                        <tr v-for="extendItem in table.extendItems" v-bind:key = "extendItem.text">
                            <td><strong>{{ extendItem.text }}:</strong> </td><td>{{ item[extendItem.value] }}</td>
                        </tr>
                    </table>
                </td>
            </template>
        </v-data-table>
   </div>
  </template>
  
<script>
import { NodeTable } from '@/assets/app/tables';

export default {
    data: () => ({
        table: new NodeTable(),
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
