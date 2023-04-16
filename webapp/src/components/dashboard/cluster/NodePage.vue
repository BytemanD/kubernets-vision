<template>
    <v-row>
        <v-col>
            <v-btn small color="primary" :disabled="table.selected.length == 0" @click="showSetDialog = true">设置标签</v-btn>
        </v-col>
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
                <template v-slot:[`item.creation`]="{ item }">
                    {{ item.creation.timestamp }}
                </template>
                <template v-slot:[`item.ready`]="{ item }">
                    <v-icon color="success" v-if="item.ready == 'True'">mdi-check-circle</v-icon>
                    <v-icon color="error" v-else>mdi-close-circle</v-icon>
                </template>
                <template v-slot:[`item.cpu`]="{ item }">
                    {{ item.allocatable.cpu }}
                </template>
                <template v-slot:[`item.memory`]="{ item }">
                    {{ Utils.parseNodeMemory(item.allocatable.memory) }}
                </template>
                <template v-slot:[`item.os_image`]="{ item }">
                    <v-chip x-small label>{{ item.os_image }}</v-chip>
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
                            <tr>
                                <td><strong>标签</strong> </td>
                                <td>
                                    <template v-for="value, key in item.labels">
                                        <v-chip small label close class="my-1 mr-1" v-if="table.hideLabels.indexOf(key) < 0"
                                            v-bind:key="key" @click:close="table.deleteLabel(item, key)">
                                            {{ key }}={{ value }}
                                        </v-chip>
                                    </template>
                                </td>
                            </tr>
                        </table>
                    </td>
                </template>
            </v-data-table>
        </v-col>
        <SetNodeLabel :show.sync="showSetDialog" :nodes.sync="table.selected" v-on:completed="updatedLabel" />
        <DescribeResource :show.sync="showDescribeDialog" resource-name='node' :resource.sync="selectNode" />
    </v-row>
</template>

<script>
import { NodeTable } from '@/assets/app/tables';
import TableRefreshBtn from '../../plugins/TableRefreshBtn';
import DescribeResource from '../dialogs/DescribeResource.vue';
import SetNodeLabel from './dialogs/SetNodeLabel';

import { Utils } from '@/assets/app/utils'

export default {
    components: {
        TableRefreshBtn, SetNodeLabel, DescribeResource
    },
    data: () => ({
        Utils: Utils,
        table: new NodeTable(),
        showSetDialog: false,
        showDescribeDialog: false,
        selectNode: null,
    }),
    methods: {
        refresh: async function () {
            this.table.refresh();
        },
        updatedLabel: function (success) {
            if (success) {
                this.refresh();
            }
        },
        describeNode: function (node) {
            this.showDescribeDialog = true;
            this.selectNode = node.name;
        }
    },
    created: async function () {
        this.refresh();
    },
};
</script>
