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
                        <v-btn text color="info">复制结果</v-btn>
                    </v-col>
                </v-row>
            </v-toolbar>
            <v-card-text style="height: 600px;">
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
        content: ''
    }),
    methods: {
        async execComamnd() {
            this.waiting = true;
            this.content = '';
            if (this.pod.containers.length >  1 && !this.container){
                MESSAGE.warning('请选择容器');
                return;
            }
            this.content = await API.action.execOnPod(this.pod.name, this.command, this.container);
            this.waiting = false;
        }
    },
    watch: {
        show(newVal) {
            this.display = newVal;
            console.log(this.display, this.pod)
            if (this.display && this.pod) {
                this.container = this.pod.containers[0].name;
            }
        },
        display(newVal) {
            this.display = newVal;
            this.$emit("update:show", this.display);
        }
    },
};
</script>
