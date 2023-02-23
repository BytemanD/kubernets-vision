<template>
    <v-btn fab x-small :color="color" v-on:click="refresh()" >
        <v-icon v-if="table.refreshing" class="mdi-spin">mdi-rotate-right</v-icon>
        <v-icon v-else>mdi-rotate-right</v-icon>
    </v-btn>
</template>


<script>

export default {
    props: {
        table: Object,
        color: {type: String, required: false, default: 'primary'}
    },
    data: () => ({
        refreshing: false,
    }),
    methods: {
        refresh: async function() {
            this.table.refresh();
        },
     },
};

</script>