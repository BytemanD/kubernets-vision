<template>
  <DashBoard/>
</template>

<script>
import axios from 'axios';
import DashBoard from './components/DashBoard';

axios.defaults.baseURL = 'http://local.kubeversion';

export default {
  name: 'KubeVision',

  components: {
    DashBoard,
  },
};
</script>
