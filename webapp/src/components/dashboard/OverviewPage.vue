<template>
  <v-row>
    <v-col>
      <v-card class="mx-auto" max-width="440" color="info">
        <v-list-item three-line>
          <v-list-item-content>
            <v-list-item-title class="headline mb-1">
              {{ clusterInfo.current_context && clusterInfo.current_context.name }}
            </v-list-item-title>
            <v-list-item-subtitle>
              {{ clusterInfo.config && clusterInfo.config.host }}
            </v-list-item-subtitle>
              <v-simple-table dense>
              <tbody>
                <tr>
                  <td><strong>git_version</strong></td>
                  <td>{{ clusterInfo.version && clusterInfo.version.git_version }}</td>
                </tr>
                <tr>
                  <td><strong>build_date</strong></td>
                  <td>{{ clusterInfo.version && clusterInfo.version.build_date }}</td>
                </tr>
                <tr>
                  <td><strong>go_version</strong></td>
                  <td>{{ clusterInfo.version && clusterInfo.version.go_version }}</td>
                </tr>
                <tr>
                  <td><strong>platform</strong></td>
                  <td>{{ clusterInfo.version && clusterInfo.version.platform }}</td>
                </tr>
              </tbody>
            </v-simple-table>
          </v-list-item-content>
          <v-list-item-avatar><v-icon large>mdi-kubernetes</v-icon></v-list-item-avatar>
        </v-list-item>
      </v-card>
    </v-col>
  </v-row>
</template>
<script>
import API from '@/assets/app/api';
import { Utils } from '@/assets/app/utils';
// import { PodTable } from '@/assets/app/tables';


export default {
  components: {

  },
  data: () => ({
    Utils: Utils,
    clusterInfo: {}
  }),
  methods: {
    refresh: async function () {
      this.clusterInfo = await API.action.getClusterInfo()
    },

  },
  created: async function () {
    this.refresh();
  },
  watch: {

  }

};
</script>
 