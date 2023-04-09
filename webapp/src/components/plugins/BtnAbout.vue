<template>
    <div>
        <v-btn text @click="onclickCallback()"> 关于</v-btn>
        <v-dialog v-model="display" width="600" scrollable>
            <v-card>
                <v-card-text>
                    <v-col>
                        <strong class="info--text mr-2">版本:</strong>{{ version.backend }}
                        <br>
                        <strong class="info--text  mr-2">项目地址:</strong>
                        <v-btn icon href="https://github.com/fjboy/kubernets-vision" target="_new">
                            <v-icon>mdi-github</v-icon>
                        </v-btn>
                        <a target="_new"
                            href="https://github.com/fjboy/kubernets-vision/blob/main/doc/ChangeLog.md">ChangeLog</a>
                    </v-col>
                </v-card-text>
            </v-card>
        </v-dialog>
    </div>
</template>

<script>
import API from '@/assets/app/api';

export default {
    data: () => ({
        display: false,
        version: {}
    }),
    methods: {
        onclickCallback: function () {
            this.display = !this.display;
            if (this.display) {
                this.getVersion();
            }
        },
        getVersion: async function () {
            this.version = (await API.version.get()).version;
        }
    },
    created() {

    }

};


</script>