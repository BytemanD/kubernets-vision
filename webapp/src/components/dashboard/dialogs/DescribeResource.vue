<template>
    <v-dialog v-model="display" width="1000" scrollable>
        <v-card>
            <v-card-title class="headline primary" primary-title>{{resourceName}}: {{ resource }}</v-card-title>
            <v-card-text>
                <HighlightCode id="describeResource" :code="yaml" />
                <!-- <pre><code>{{ yaml }}</code></pre> -->
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
        resourceName: String,
        resource: String,
    },
    components: {
        HighlightCode,
    },
    data: () => ({
        display: false,
        yaml: ''
    }),
    methods: {
        describeResource: async function(){
            let data = '';
            switch (this.resourceName){
                case 'node':
                    data = (await API.node.get(`${this.resource}?format=yaml`)).node; break;
                case 'daemonset':
                    data = (await API.daemonset.get(`${this.resource}?format=yaml`)).daemonset; break;
                case 'deployment':
                    data = (await API.deployment.get(`${this.resource}?format=yaml`)).deployment; break;
                case 'pod':
                    data = (await API.pod.get(`${this.resource}?format=yaml`)).pod; break;
                case 'namespace':
                    data = (await API.namespace.get(`${this.resource}?format=yaml`)).namespace; break;
                case 'configmap':
                    data = (await API.configmap.get(`${this.resource}?format=yaml`)).configmap; break;
                case 'service':
                    data = (await API.service.get(`${this.resource}?format=yaml`)).service; break;
                default:
                    throw Error(`未知的资源 ${this.resourceName}`);
            }
            this.yaml = data
        }
     },
    watch: {
        show(newVal) {
            this.display = newVal;
            if (this.display && this.resourceName){
                this.describeResource();
            }
        },
        display(newVal) {
            this.display = newVal;
            this.$emit("update:show", this.display);
        }
    },
};
</script>
