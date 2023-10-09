<template>
  <DashBoard/>
</template>

<script>
import Init from '@/assets/app/init';
import DashBoard from './components/DashBoard';


export default {
  name: 'KubeVision',

  components: {
    DashBoard,
  },
  methods: {

  },
  created() {
    Init()
  },
  mounted() {
    // this.showMessage({title: '测试'})
    // SimpleMessage.success('this is message')
  }
};

</script>
