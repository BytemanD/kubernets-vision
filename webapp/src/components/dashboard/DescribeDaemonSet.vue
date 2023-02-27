<template>
    <v-dialog v-model="display" width="1000" scrollable>
        <v-card>
            <v-card-title class="headline grey lighten-2" primary-title>DaemonSet：{{ daemonset }}</v-card-title>
            <v-card-text><pre class="white--text grey darken-3 pa-4">{{ yaml }}</pre></v-card-text>
        </v-card>
    </v-dialog>
</template>

<script>
import API from '@/assets/app/api';

export default {
    props: {
        show: Boolean,
        daemonset: String,
    },
    data: () => ({
        display: false,
        yaml: ''
    }),
    methods: {
        refresh: async function(daemonset){
            let data = (await API.daemonset.get(`${daemonset}?format=yaml`))
            this.yaml = data.daemonset
        }
     },
    watch: {
        show(newVal) {
            this.display = newVal;
            if (this.display && this.daemonset){
                this.refresh(this.daemonset);
            }
        },
        display(newVal) {
            this.display = newVal;
            this.$emit("update:show", this.display);
        }
    },
};
</script>
