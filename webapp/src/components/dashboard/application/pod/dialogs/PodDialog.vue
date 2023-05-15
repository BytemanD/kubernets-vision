<template>
    <v-dialog v-model="display" scrollable>
        <v-card>
            <v-toolbar dense class="primary darken-2 white--text">
                容器组 {{ pod.name }}<v-spacer></v-spacer>
                <span class="grey--text">{{ pod.creation && pod.creation.timestamp }}</span>
            </v-toolbar>
            <v-card-text style="height: 600px;" class="pt-4">
                <v-row>
                    <v-col>
                        <h4>所在节点</h4>{{ pod.node_name }}
                    </v-col>
                    <v-col>
                        <h4>容器组IP</h4> {{ pod.pod_ip }}
                    </v-col>
                    <v-col>
                        <h4>阶段</h4> {{ pod.phase }}
                    </v-col>
                </v-row>
                <v-row>
                    <v-col cols="12" v-for="container in pod.containers" v-bind:key="container.name">
                        <v-sheet elevation="2" class="pa-4">
                            <v-row>
                                <v-col cols="4">
                                    <v-chip label small color="primary darken-1">容器</v-chip>{{ container.name }}
                                </v-col>
                                <v-col cols="4">
                                    <template v-for="port in container.ports" >
                                        <KVChip v-bind:key="port.container_port" :name="port.protocol" :value="port.container_port" small></KVChip>
                                    </template>
                                </v-col>
                                <v-col cols="4">
                                    <!-- <v-btn x-small class="pa-1" color="grey"><v-icon small>mdi-console-line</v-icon></v-btn>
                                    <v-btn x-small class="pa-1 ml-2" color="grey"><v-icon>mdi-cards-variant</v-icon></v-btn>
                                    <v-btn x-small class="pa-1 ml-2" color="primary"><v-icon>mdi-database</v-icon></v-btn>
                                    <v-btn x-small class="pa-1 ml-2" color="error"><v-icon>mdi-information</v-icon></v-btn> -->
                                </v-col>
                                <v-col cols="12">
                                    <span class="grey--text">镜像抓取策略: {{ container.image_pull_policy }}</span>
                                    <span class="grey--text ma-6">镜像: {{ container.image }}</span>
                                </v-col>
                            </v-row>
                        </v-sheet>
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import API from '@/assets/app/api';
import MESSAGE from '@/assets/app/message';

import KVChip from '@/components/plugins/KVChip.vue';


export default {
    props: {
        show: Boolean,
        pod: Object,
    },
    components: {
        KVChip,
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
