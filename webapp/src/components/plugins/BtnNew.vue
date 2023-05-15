<template>
    <div>
        <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
                <v-btn icon color="primary" @click="onclickCallback()" v-bind="attrs" v-on="on">
                    <v-icon>mdi-plus</v-icon>
                </v-btn>
            </template>
            新建
        </v-tooltip>
        <v-dialog v-model="display" width="800" scrollable>
            <v-card>
                <v-card-text class="pa-1">
                    <v-textarea class="mt-1" outlined rows="16" v-model='workflow' placeholder="请输入配置(备注:目前仅支持yaml格式)"></v-textarea>
                </v-card-text>
                <v-divider></v-divider>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn @click="commit()">创建</v-btn>
                </v-card-actions>
            </v-card>
        </v-dialog>
    </div>
</template>

<script>
import API from '@/assets/app/api';
import MESSAGE from '@/assets/app/message';

export default {
    data: () => ({
        display: false,
        workflow: ''
    }),
    methods: {
        onclickCallback: function () {
            this.display = !this.display;
        },
        commit: async function(){
            await API.createWorkload(this.workflow);
            MESSAGE.success('创建成功')
        }
    },
    created() {

    }

};


</script>