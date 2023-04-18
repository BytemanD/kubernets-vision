<template>
    <v-row>
        <v-col></v-col>
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
                <template v-slot:[`item.data_nums`]="{ item }">
                    <v-chip x-small label>{{ item.data_list.length }}</v-chip>
                </template>
                <template v-slot:[`item.creation`]="{ item }">
                    {{ item.creation.timestamp }}
                </template>
                <template v-slot:[`item.actions`]="{ item }">
                    <v-menu offset-y>
                        <template v-slot:activator="{ on, attrs }">
                            <v-btn icon color="purple" v-bind="attrs" v-on="on"><v-icon
                                    small>mdi-dots-vertical</v-icon></v-btn>
                        </template>
                        <v-list dense>
                            <v-list-item @click="describeResource(item)">
                                <v-list-item-title>YAML</v-list-item-title>
                            </v-list-item>
                            <v-list-item @click="showConfigMap(item)">
                                <v-list-item-title>查看</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                </template>
                <template v-slot:[`expanded-item`]="{ headers, item }">
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
        <DescribeResource :show.sync="showDescribeDialog" resource-name='configmap' :resource="selectResource" />
        <ShowConfigMap :show.sync="showConfigMapDialog" :resource="selectResource" />
    </v-row>
</template>

<script>
import { ConfigMapTable } from '@/assets/app/tables';

import TableRefreshBtn from '../../plugins/TableRefreshBtn.vue';
import ShowConfigMap from './dialogs/ShowConfigMap.vue';
import DescribeResource from '../dialogs/DescribeResource.vue';

export default {
    components: {
        TableRefreshBtn,
        DescribeResource, ShowConfigMap,
    },
    data: () => ({
        table: new ConfigMapTable(),
        selectResource: null,
        showDescribeDialog: false,
        showConfigMapDialog: false,
    }),
    methods: {
        refresh: async function () {
            this.table.refresh();
        },
        describeResource: function (item) {
            this.showDescribeDialog = !this.showDescribeDialog;
            this.selectResource = item.name;
        },
        showConfigMap: function (item) {
            this.showConfigMapDialog = !this.showConfigMapDialog;
            this.selectResource = item.name;
        }

    },
    created: async function () {
        this.refresh();
    },
};
</script>
