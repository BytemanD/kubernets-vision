<template>
    <v-dialog v-model="display" width="1200" scrollable>
        <v-card>
            <v-card-text class="pt-2" height="500">
                <v-row>
                    <v-col cols="3">
                        <v-list-item-group color="primary">
                            <v-list-item v-for="(value, name) in configMap.data" v-bind:key="name" @click="selectConfigData(name)">
                                <v-list-item-content>
                                    <v-list-item-title >{{ name }}</v-list-item-title>
                                </v-list-item-content>
                            </v-list-item>
                        </v-list-item-group>
                    </v-col>
                    <v-col cols="9">
                        <HighlightCode id="configMapCode" :code="configMapData" />
                    </v-col>
                </v-row>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import API from '@/assets/app/api';

import HighlightCode from '@/components/plugins/HighlightCode.vue';

export default {
    props: {
        show: Boolean,
        resource: String,
    },
    components: {
        HighlightCode,
    },
    data: () => ({
        display: false,
        itemIndex: 0,
        configMap: {},
        key: null,
        selectConfigName: null,
        configData: {data: {}},
        configMapData: '',
    }),
    methods: {
        getConfigMap: async function () {
            this.configMap = (await API.configmap.get(this.resource)).configmap;
            if (Object.keys(this.configMap.data).length == 0) {
                this.key = null;
            } else {
                this.key = Object.keys(this.configMap.data)[0];
            }
        },
        selectConfigData: function(name){
            this.selectConfigName = name;
            this.configMapData = this.configMap.data[this.selectConfigName];
        }
    },
    watch: {
        show(newVal) {
            this.display = newVal;
            if (this.display && this.resource) {
                this.getConfigMap()
            }
        },
        display(newVal) {
            this.display = newVal;
            this.$emit("update:show", this.display);
        }
    },
};
</script>
