<template>
    <v-dialog v-model="display" width="1000" scrollable>
        <v-card>
            <v-card-title class="headline primary lighten-2" primary-title>
                {{ resourceName }}: {{ resource.name }}</v-card-title>
            <v-card-text class="pt-4">
                <v-text-field outlined v-for="container in resource.containers" v-bind:key="container.name"
                    :label="container.name" :value="container.image" v-model="container.image"></v-text-field>
                <!-- <v-text-field hide-details label="镜像" v-model="newImage"></v-text-field> -->
                <v-switch label="强制" v-model="force"></v-switch>
            </v-card-text>
            <v-divider></v-divider>
            <v-card-title>
                <v-spacer></v-spacer><v-btn @click="replace()">替换</v-btn>
            </v-card-title>
        </v-card>
    </v-dialog>
</template>

<script>
import API from '@/assets/app/api';
import MESSAGE from '@/assets/app/message';

export default {
    props: {
        show: Boolean,
        resourceName: String,
        resource: Object,
    },
    data: () => ({
        display: false,
        newImage: null,
        force: false,
    }),
    methods: {
        replace: async function () {
            switch (this.resourceName) {
                case 'node':
                    await API.node.put(`${this.resource.name}`), { daemonset: {} };
                    break;
                case 'daemonset':
                    var containders = {};
                    for (let i in this.resource.containers) {
                        let container = this.resource.containers[i];
                        containders[container.name] = container;
                    }
                    var data = { force: this.force, containers: containders }
                    await API.daemonset.put(this.resource.name, { daemonset: data });
                    MESSAGE.success(`${this.resourceName} 替换成功`)
                    this.$emit('completed');
                    this.display = false;
                    break;
            }
        }
    },
    watch: {
        show(newVal) {
            this.display = newVal;
        },
        display(newVal) {
            this.display = newVal;
            this.$emit("update:show", this.display);
        }
    },
};
</script>
