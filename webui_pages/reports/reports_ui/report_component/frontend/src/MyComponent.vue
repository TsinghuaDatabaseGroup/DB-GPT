<template>
  <div class="wrapper">
    <!-- 
      Show a button and some text.
      When the button is clicked, we'll increment our "numClicks" state
      variable, and send its new value back to Streamlit, where it'll
      be available to the Python program.
    -->
    <span>
      Hello, {{args.name}}! &nbsp;
      <button v-on:click="onClicked()">Click Me!</button>
    </span>
  </div>
</template>

<script>
import { Streamlit } from "streamlit-component-lib";

export default {
  name: "MyComponent",
  props: ["args"], // Arguments that are passed to the plugin in Python are accessible in props `args`. Here, we access the "name" arg.
  data() {
    return {
      numClicks: 0
    };
  },
  methods: {
    /** Click handler for our "Click Me!" button. */
    onClicked: function() {
      // Increment this.numClicks, and pass the new value back to
      // Streamlit via `Streamlit.setComponentValue`.
      this.numClicks++;
      Streamlit.setComponentValue(this.numClicks);
    }
  }
};
</script>
