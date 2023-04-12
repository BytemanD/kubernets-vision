<template>
  <v-row>
    {{ clusterInfo }}
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
 