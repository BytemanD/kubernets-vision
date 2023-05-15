<template>
    <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
            <v-btn icon v-on:click="onclickCallback()" v-bind="attrs" v-on="on">
                <v-icon v-if="$vuetify.theme.dark">mdi-weather-night</v-icon>
                <v-icon v-else>mdi-weather-sunny</v-icon>
            </v-btn>
        </template>
        切换主题(明亮/暗黑)
    </v-tooltip>
</template>

<script>

let itemThemeDark = 'themeDark';

export default {
    methods: {
        getThemeDark: function(){
            return localStorage.getItem(itemThemeDark) == 'true';
        },
        onclickCallback: function () {
            this.$vuetify.theme.dark = !this.$vuetify.theme.dark;
            localStorage.setItem(itemThemeDark, this.$vuetify.theme.dark)
        }
    },
    created() {
        this.$vuetify.theme.dark = this.getThemeDark();
    }

};


</script>