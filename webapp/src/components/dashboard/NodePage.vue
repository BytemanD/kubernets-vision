<template>
    <v-row>
        <v-col>
            <v-btn small color="primary" :disabled="table.selected.length == 0" @click="showSetDialog = true">添加标签</v-btn>
        </v-col>
        <v-col>
            <v-text-field small dense single-line hide-details v-model="table.search" append-icon="mdi-magnify" label="搜索"></v-text-field>
        </v-col>
        <v-col cols="2">
            <TableRefreshBtn :table="table" />
        </v-col>
        <v-col cols="12">
            <v-data-table dense :headers="table.headers" :items="table.items" item-key="name"
                :items-per-page="table.itemsPerPage" :search="table.search" show-select v-model="table.selected" show-expand
                single-expand>

                <template v-slot:[`item.name`]="{ item }">
                    <v-chip small label class="info"> {{ item.name }}</v-chip>
                </template>
                <template v-slot:[`item.os_image`]="{ item }">
                    <v-chip x-small label>{{ item.os_image }}</v-chip>
                </template>
                <template v-slot:[`item.labels`]="{ item }">
                    <template v-for="value, key in item.labels">
                        <v-chip small label close v-if="table.hideLabels.indexOf(key) < 0" v-bind:key="key"
                            class="my-1 mr-1" @click:close="table.deleteLabel(item, key)">{{ key }}={{ value }}</v-chip>
                    </template>
                </template>

                <template v-slot:[`expanded-item`]="{ headers, item }">
                    <td></td>
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
        <SetNodeLabel :show.sync="showSetDialog" :nodes.sync="table.selected" v-on:completed="updatedLabel" />
    </v-row>
</template>

<script>
import { NodeTable } from '@/assets/app/tables';
import TableRefreshBtn from '../plugins/TableRefreshBtn';
import SetNodeLabel from './SetNodeLabel';

export default {
    components: {
        TableRefreshBtn, SetNodeLabel,
    },
    data: () => ({
        table: new NodeTable(),
        showSetDialog: false,
    }),
    methods: {
        refresh: async function () {
            this.table.refresh();
        },
        updatedLabel: function (value) {
            if (value) {
                this.$MESSAGE.success('添加成功');
                this.refresh();
            } else {
                this.$MESSAGE.error('添加失败');
            }
        }
    },
    created: async function () {
        this.refresh();
    },
};
</script>
