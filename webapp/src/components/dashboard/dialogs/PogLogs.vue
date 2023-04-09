<template>
    <v-dialog v-model="display" width="1000" scrollable>
        <v-card>
            <v-card-title class="headline primary" primary-title>
                <v-col class="my-0 py-0">{{ pod.name }}</v-col>
                <v-col cols='6' class="my-0 py-0">
                    <v-select solo flat hide-details dense class="pa-0 ma-0" :items="pod.containers" prefix='选择容器:'
                        item-text="name" v-model="container" v-on:change="refreshLogs()">
                    </v-select>
                </v-col>
                <v-col cols='2' class="my-0 py-0">
                    <v-btn small class="my-0 py-0" @click="refreshLogs()">刷新</v-btn>
                </v-col>
            </v-card-title>
            <v-card-text>
                <pre>{{ content }}</pre>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import API from '@/assets/app/api';

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
            this.content = await (API.logs.get(this.pod.name, this.container));
        }
    },
    watch: {
        show(newVal) {
            this.display = newVal;
            if (this.display && this.pod) {
                if (this.pod.containers.length == 1) {
                    this.container = this.pod.containers[0].name;
                } else {
                    this.container = null;
                }
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
