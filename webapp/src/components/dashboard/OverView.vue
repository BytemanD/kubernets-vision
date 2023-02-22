<template>
    <v-row>
        <v-col>
            <v-btn small color="primary" :disabled="table.selected.length == 0" @click="showSetDialog = true">设置标签</v-btn>
        </v-col>
        <v-col cols="2">
            <v-btn fab x-small color="info" v-on:click="table.refresh()" >
                <v-icon v-if="table.refreshing" class="mdi-spin">mdi-rotate-right</v-icon>
                <v-icon v-else>mdi-rotate-right</v-icon>
            </v-btn>
        </v-col>
        <v-col cols="12">
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
                        <v-chip small label close v-if="table.hideLabels.indexOf(key) < 0" v-bind:key="key" class="my-1 mr-1"
                            @click:close="table.deleteLabel(item, key)">{{key}}={{value}}</v-chip>
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
        </v-col>
        <SetNodeLabel :show.sync="showSetDialog" :nodes.sync="table.selected" v-on:completed="updatedLabel" />
    </v-row>
</template>

<script>
import { NodeTable } from '@/assets/app/tables';
import SetNodeLabel from './SetNodeLabel';

export default {
    components: {
        SetNodeLabel,
    },
    data: () => ({
        table: new NodeTable(),
        showSetDialog: false,
    }),
    methods: {
        refresh: async function() {
            this.table.refresh();
        },
        updatedLabel: function(value){
            if (value){
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
