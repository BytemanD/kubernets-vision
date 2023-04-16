<template>
    <v-row>
        <v-col>有状态副本集 TODO</v-col>
    </v-row>
</template>

<script>
import { Utils } from '@/assets/app/utils';

import { DaemonsetTable } from '@/assets/app/tables';

export default {
    components: {
        
    },
    props: {
        namespace: String
    },
    data: () => ({
        Utils: Utils,
        table: new DaemonsetTable(),
        showDescribeDialog: false,
        showReplaceDialog: false,
        selectDaemonset: null,
        selectedItem: {},
    }),
    methods: {
        refresh: async function () {
            this.table.refresh();
        },
        describeDaemonSet: function (item) {
            this.showDescribeDialog = !this.showDescribeDialog;
            this.selectDaemonset = item.name;
        },
        replaceDaemonSet: function (item) {
            this.showReplaceDialog = !this.showReplaceDialog;
            this.selectedItem = item;
        }
    },
    created: async function () {
        this.refresh();
    },
    watch: {
        namespace(newValue) {
            this.table.namespace = newValue;
            this.table.refresh();
        }
    }
};
</script>
 