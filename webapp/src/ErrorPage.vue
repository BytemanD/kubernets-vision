<template>
    <v-app>
        <v-main>
            <v-row text-center class="my-auto">
                <v-col class="mx-auto my-auto">
                    <v-alert text color="error">
                        <div class="title">{{ title }}</div>
                        <div>{{ error }}</div>
                    </v-alert>
                </v-col>
            </v-row>
        </v-main>
    </v-app>
</template>

<script>
export default {
    props: {
        title: String,
        error: Error
    },
};
</script>
