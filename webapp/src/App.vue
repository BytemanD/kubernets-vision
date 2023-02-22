<template>
  <DashBoard/>
</template>

<script>
import axios from 'axios';
import DashBoard from './components/DashBoard';


axios.defaults.baseURL = 'http://kubevision.local';

// Vue.prototype.$message = SimpleMessage.install;


export default {
  name: 'KubeVision',

  components: {
    DashBoard,
  },
  methods: {

  },
  mounted() {
    // this.showMessage({title: '测试'})
    // SimpleMessage.success('this is message')
  }
};

</script>
