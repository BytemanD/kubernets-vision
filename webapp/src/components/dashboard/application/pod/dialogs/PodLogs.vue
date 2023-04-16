<template>
    <v-dialog v-model="display" width="1200" scrollable>
        <v-card>
            <v-toolbar>
                <v-row class="mt-4 mb-4">
                    <v-col cols="6">
                        <v-select hide-details class="pa-0 ma-0" :items="pod.containers" prefix='选择容器:' item-text="name" v-model="container"
                            v-on:change="refreshLogs()"></v-select>
                    </v-col>
                    <v-col cols="2">
                        <v-btn color="info" class="my-0 py-0" @click="refreshLogs()">刷新</v-btn>
                    </v-col>
                </v-row>
            </v-toolbar>
            <v-card-text style="height: 600px;" class="pt-4">
                <pre>{{ content }}</pre>
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
        content: ''
    }),
    methods: {
        async refreshLogs() {
            if (this.pod.containers.length > 1 && !this.container) {
                MESSAGE.warning('请选择容器')
                return;
            }
            this.content = await (API.action.getLog(this.pod.name, this.container));
        }
    },
    watch: {
        show(newVal) {
            this.display = newVal;
            if (this.display && this.pod) {
                this.content = '';
                this.container = this.pod.containers[0].name;
                if (this.pod.containers.length == 1 || this.container) {
                    this.refreshLogs();
                }
            }
        },
        display(newVal) {
            this.display = newVal;
            this.$emit("update:show", this.display);
        }
    },
};
</script>
