<template>
    <v-dialog v-model="display" scrollable>
        <v-card>
            <v-toolbar>
                <v-spacer></v-spacer>
                <v-col cols="6">
                    <v-switch hide-details label="高亮" v-model="hightlight"></v-switch>
                </v-col>
                <v-col cols="6">
                    <v-select hide-details dense outlined prefix='配置:' v-model="selectConfigName"
                        :items="Object.keys(configMap.data || {})"
                        v-on:change="selectConfigData(selectConfigName)"></v-select>
                </v-col>
            </v-toolbar>
            <v-card-text class="pt-2">
                <div style="height: 480px">
                    <HighlightCode id="configMapCode" :code="configMapData" :hightlight="hightlight" />
                </div>
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
        hightlight: false,
        selectConfigName: null,
        configData: { data: {} },
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
        selectConfigData: function (name) {
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
