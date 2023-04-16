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
                <template v-slot:[`item.ports`]="{ item }">
                    <v-chip x-small color="indigo" text-color="white" v-for="port in item.ports" v-bind:key="port.port">
                        {{  port.protocol }} {{ port.target_port }}:{{ port.port }}
                    </v-chip>
                </template>
                <template v-slot:[`item.actions`]="{ item }">
                    <v-menu offset-y>
                        <template v-slot:activator="{ on, attrs }">
                            <v-btn icon color="purple" v-bind="attrs" v-on="on"><v-icon
                                    small>mdi-dots-vertical</v-icon></v-btn>
                        </template>
                        <v-list dense>
                            <v-list-item @click="describeNode(item)">
                                <v-list-item-title>描述</v-list-item-title>
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
    </v-row>
</template>

<script>
import { ServiceTable } from '@/assets/app/tables';

import TableRefreshBtn from '@/components/plugins/TableRefreshBtn.vue';

export default {
    components: {
        TableRefreshBtn
    },
    data: () => ({
        table: new ServiceTable(),
        showSetDialog: false,
        showDescribeDialog: false,
        selectNode: null,
    }),
    methods: {
        refresh: async function () {
            this.table.refresh();
        },

    },
    created: async function () {
        this.refresh();
    },
};
</script>
