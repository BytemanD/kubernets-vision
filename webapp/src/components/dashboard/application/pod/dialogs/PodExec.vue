<template>
    <v-dialog v-model="display" width="1200" scrollable>
        <v-card>
            <v-toolbar>
                <v-row class="mt-4 mb-4">
                    <v-col cols="3">
                        <v-select  hide-details :items="pod.containers" prefix='容器:' item-text="name" v-model="container"></v-select>
                    </v-col>
                    <v-col>
                        <v-text-field  hide-details prefix="命令:" v-model="command"></v-text-field>
                    </v-col>
                    <v-col cols="2">
                        <v-btn color="warning" class="mr-1" :disabled="command.length==0"  @click="execComamnd()" >执行</v-btn>
                        <!-- <v-btn text color="info">复制结果</v-btn> -->
                        <v-menu offset-y>
                            <template v-slot:activator="{ on, attrs }">
                                <v-btn text color="purple" v-bind="attrs" v-on="on" @click="refresExecHistory()">历史</v-btn>
                        </template>
                        <v-list dense>
                            <v-list-item v-for="cmd in history" v-bind:key="cmd" @click="inputComand(cmd)" >
                                <v-list-item-title>{{ cmd }}</v-list-item-title>
                            </v-list-item>
                        </v-list>
                    </v-menu>
                    
                    </v-col>
                </v-row>
            </v-toolbar>
            <v-card-text style="height: 600px;" class="pt-4">
                <v-icon class="mdi-spin" v-if="waiting">mdi-rotate-right</v-icon>
                <pre v-else>{{ content }}</pre>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import API from '@/assets/app/api';
import MESSAGE from '@/assets/app/message';

export default {
    props: {
        show: Boolean,
        pod: Object,
    },
    data: () => ({
        display: false,
        container: null,
        waiting: false,
        command: '',
        content: '',
        history: []
    }),
    methods: {
        async execComamnd() {
            this.waiting = true;
            this.content = '';
            if (this.pod.containers.length >  1 && !this.container){
                MESSAGE.warning('请选择容器');
                return;
            }
            let cmd = this.command.trim();
            this.content = await API.action.execOnPod(this.pod.name, cmd, this.container);
            this.waiting = false;
            if (this.history.indexOf(cmd) < 0){
                API.action.addExecHistory(cmd);
                this.history.unshift(cmd)
            }
        },
        async refresExecHistory(){
            this.history = await API.action.getExecHistory();
        },
        inputComand(cmd){
            this.command = cmd;
        }
    },
    watch: {
        show(newVal) {
            this.display = newVal;
            this.command = '';
            this.content = '';
            if (this.display && this.pod) {
                this.container = this.pod.containers[0].name;
                this.refresExecHistory();
            }
        },
        display(newVal) {
            this.display = newVal;
            this.$emit("update:show", this.display);
        }
    },
};
</script>
