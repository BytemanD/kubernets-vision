<template>
    <div>
        <v-tooltip bottom>
            <template v-slot:activator="{ on, attrs }">
                <v-btn icon color="warning" @click="onclickCallback()" v-bind="attrs" v-on="on">
                    <v-icon>mdi-bell</v-icon>
                </v-btn>
            </template>
            事件
        </v-tooltip>
        <v-dialog v-model="display" scrollable>
            <v-card>
                <v-card-text>
                    <EventDialogVue />
                </v-card-text>
            </v-card>
        </v-dialog>
    </div>
</template>

<script>
import EventDialogVue from '../dashboard/dialogs/EventDialog.vue';

export default {
    data: () => ({
        display: false,
    }),
    components: {
        EventDialogVue
    },
    methods: {
        onclickCallback: function () {
            this.display = !this.display;
        },
    },
};


</script>