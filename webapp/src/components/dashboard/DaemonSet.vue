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
            <v-data-table dense :headers="table.headers" :items="table.items" item-key="name"
               :items-per-page="table.itemsPerPage" :search="table.search"
               show-select v-model="table.selected" show-expand single-expand>

               <template v-slot:[`item.node_selector`]="{ item }">
                  <v-chip x-small label v-bind:key="key" v-for="value, key in item.node_selector" class="mr-2">{{key}}={{value}}</v-chip>
               </template>
               <template v-slot:[`item.selector`]="{ item }">
                   <v-chip x-small label v-bind:key="key" v-for="value, key in item.selector" class="mr-2">{{key}}={{value}}</v-chip>
               </template>
               <template v-slot:[`item.actions`]="{ item }">
                    <v-btn x-small @click="describeDaemonSet(item)">描述</v-btn>
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
        </v-col>
        <DescribeDaemonSet :show.sync="showDescribeDialog" :daemonset.sync="selectDaemonset" />
    </v-row>
</template>

<script>
import { DaemonsetTable } from '@/assets/app/tables';
import TableRefreshBtn from '../plugins/TableRefreshBtn';
import DescribeDaemonSet from './DescribeDaemonSet';

export default {
    components: {
        TableRefreshBtn, DescribeDaemonSet
    },
    props: {
        namespace: String
    },
    data: () => ({
         table: new DaemonsetTable(),
         showDescribeDialog: false,
         selectDaemonset: null,
     }),
     methods: {
      refresh: async function() {
          this.table.refresh();
       },
       describeDaemonSet: function(item){
            this.showDescribeDialog = true;
            this.selectDaemonset = item.name;
        }
    },
    created: async function () {
         this.refresh();
    },
    watch: {
        namespace(newValue){
            this.table.namespace = newValue;
            this.table.refresh();
        }
    }
 };
 </script>
 