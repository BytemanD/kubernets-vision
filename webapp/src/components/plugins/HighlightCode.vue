<template>
  <div style="overflow-y: scroll">
    <tr>
      <td class="blue-grey lighten-1 white--text px-1 text-right">
        <span v-for="index of lines" v-bind:key="index">{{ index }} <br /></span>
      </td>
      <td style="width: 100%;">
        <pre :id="id"><code class="hljs"></code></pre>
      </td>
    </tr>
  </div>
</template>

<script>
// import 'highlight.js/styles/stackoverflow-light.css'
// import 'highlight.js/styles/dark.css'
import 'highlight.js/styles/atom-one-dark.css'
import hljs from 'highlight.js';

export default {
  props: {
    id: String,
    code: String,
    hightlight: { type: Boolean, default: false },
  },
  data: () => ({
    loading: false,
    preNode: null,
    codeNode: null,
    lines: 0,
    wrapRegex: new RegExp('\\n', 'g'),
  }),
  methods: {
    getCodeLines: function () {
      this.lines = 0;
      Array.from(this.code.matchAll(this.wrapRegex), () => this.lines++);
    },
    setCode: function () {
      if (this.hightlight) {
        let self = this;
        setTimeout(
          function () {
            let hljsCode = hljs.highlightAuto(self.code);
            self.codeNode.innerHTML = hljsCode.value;
          }, 1)
      } else {
        this.codeNode.innerHTML = this.code;
      }
    }
  },
  watch: {
    code(newValue) {
      // TODO: 无效
      this.loading = true;
      this.lines = 0;
      if (!this.codeNode) {
        this.preNode = document.getElementById(this.id);
        this.codeNode = this.preNode.childNodes[0];
      }
      if (newValue) {
        this.setCode()
        this.getCodeLines();
        this.loading = false;
      }
    },
  }
};
</script>
