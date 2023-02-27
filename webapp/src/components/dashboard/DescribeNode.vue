<template>
    <v-dialog v-model="display" width="1000" scrollable>
        <v-card>
            <v-card-title class="headline grey lighten-2" primary-title>节点：{{ node }}</v-card-title>
            <v-card-text><pre class="white--text grey darken-3 pa-4">{{ yaml }}</pre></v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import API from '@/assets/app/api';

export default {
    props: {
        show: Boolean,
        node: String,
    },
    data: () => ({
        display: false,
        yaml: ''
    }),
    methods: {
        refreshNode: async function(node){
            let data = (await API.node.get(`${node}?format=yaml`))
            this.yaml = data.node
        }
     },
    watch: {
        show(newVal) {
            this.display = newVal;
            if (this.display && this.node){
                this.refreshNode(this.node);
            }
        },
        display(newVal) {
            this.display = newVal;
            this.$emit("update:show", this.display);
        }
    },
};
</script>
