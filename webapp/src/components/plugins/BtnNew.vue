<template>
    <div>
        <v-tooltip top>
            <template v-slot:activator="{ on, attrs }">
                <v-btn icon color="primary" @click="onclickCallback()" v-bind="attrs" v-on="on">
                    <v-icon>mdi-plus</v-icon>
                </v-btn>
            </template>
            新建工作负载
        </v-tooltip>
        <v-dialog v-model="display" width="800" scrollable>
            <v-card>
                <v-card-title class="primary">
                    创建工作负载
                    <v-spacer></v-spacer>
                    <v-btn>创建</v-btn>
                </v-card-title>
                <v-card-text class="pa-1">
                    <v-textarea class="mt-1" outlined v-model='workflow' placeholder="请输入工作负载配置(目前仅支持yaml格式)"></v-textarea>
                </v-card-text>
                <v-divider></v-divider>
                <v-card-actions>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script>
import API from '@/assets/app/api';

export default {
    data: () => ({
        display: false,
        workflow: ''
    }),
    methods: {
        onclickCallback: function () {
            this.display = !this.display;
            if (this.display) {
                this.getVersion();
            }
        },
        getVersion: async function () {
            this.version = (await API.version.get()).version;
        }
    },
    created() {

    }

};


</script>