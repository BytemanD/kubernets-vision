<template>
    <v-dialog v-model="display" width="600">
        <v-card>
            <v-card-title class="headline grey lighten-2" primary-title>添加标签</v-card-title>
            <v-card-text>
                <h3>节点</h3>
                <v-chip label v-for="node in selectedNodes" v-bind:key="node.name">{{ node.name }}</v-chip>
                <h3>请输入标签</h3>
                <v-textarea class="mt-1" solo v-model='labels' label="标签" ></v-textarea>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="primary" @click="commit()">添加</v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<script>
import API from '@/assets/app/api';

export default {
    props: {
        show: Boolean,
        nodes: Array,
    },
    data: () => ({
        display: false,
        selectedNodes: [],
        labels: ''
    }),
    methods: {
        commit: async function() {
            try {
                let labels = {}
                let lines = this.labels.split('\n');
                for (let i in lines){
                    let values = lines[i].split('=')
                    labels[values[0]] = values.length >= 2 ? values[1]: null;
                }
                if (labels.length == 0){
                    return;
                }
                for (let i in this.nodes){
                    let node = this.nodes[i];
                    await API.addNodeLabels(node.name, labels);
                }
                this.$emit("completed", true);
            } catch {
                this.$emit("completed", false);
            }
       }
     },
    watch: {
        show(newVal) {
            this.display = newVal;
        },
        nodes(newVal) {
            this.selectedNodes = newVal;
        },
        display(newVal) {
            this.display = newVal;
            this.$emit("update:show", this.display);
        }
    },
    created: async function () {
        // this.refresh();
    },
};
</script>
