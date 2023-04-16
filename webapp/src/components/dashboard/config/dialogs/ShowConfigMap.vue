<template>
    <v-dialog v-model="display" width="1200" scrollable>
        <v-card>
            <v-card-text class="pt-2" height="400">
                <v-expansion-panels>
                    <v-expansion-panel v-for="(value, key) in configMap.data" v-bind:key="key">
                        <v-expansion-panel-header>
                            {{ key }}
                        </v-expansion-panel-header>
                        <v-expansion-panel-content>
                            <pre class="white--text grey darken-3 pa-4">{{ value }}</pre>
                        </v-expansion-panel-content>
                    </v-expansion-panel>
                </v-expansion-panels>
            </v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import API from '@/assets/app/api';

export default {
    props: {
        show: Boolean,
        resource: String,
    },
    data: () => ({
        display: false,
        itemIndex: 0,
        configMap: {},
        key: null,
    }),
    methods: {
        getConfigMap: async function () {
            this.configMap = (await API.configmap.get(this.resource)).configmap;
            if (Object.keys(this.configMap.data).length == 0) {
                this.key = null;
            } else {
                this.key = Object.keys(this.configMap.data)[0];
            }
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
