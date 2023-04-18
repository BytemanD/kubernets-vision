<template>
  <div style="height:400px; overflow-y: scroll">
    <pre :id="id"><code class="hljs"></code></pre>
  </div>
</template>

<script>
import 'highlight.js/styles/stackoverflow-light.css'
import hljs from 'highlight.js';

export default {
  props: {
    id: String,
    code: String,
  },
  data: () => ({
    loading: false,
    preNode: null,
    codeNode: null,
  }),
  created() {

  },
  watch: {
    code(newValue) {
      // TODO: 无效
      this.loading = true;
      if (!this.codeNode){
        this.preNode = document.getElementById(this.id)
        this.codeNode = this.preNode.childNodes[0];
      }
      this.codeNode.innerHTML = '';
      if (newValue) {
        let hljsCode = hljs.highlightAuto(this.code);
        this.codeNode.innerHTML = hljsCode.value;
      }
      this.loading = false;
    },
  }
};
</script>
