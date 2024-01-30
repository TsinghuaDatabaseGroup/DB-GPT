<!--
  We bootstrap our Component to Streamlit with our scoped slot in the top-level App.
  This is where scoped slot passes Streamlit ;`args` data from itself to children MyComponent.
  You should not have to edit this, but are free to do so :)
-->
<template>
  <div id="app">
    <WithStreamlitConnection v-slot="{ args }">
      <ReportFlow :args="args" />
    </WithStreamlitConnection>
  </div>
</template>

<script>
import ReportFlow from "./report_flow.vue";

// "withStreamlitConnection" is a scoped slot. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
//
// You don't need to edit withStreamlitConnection (but you're welcome to!).
import WithStreamlitConnection from "./streamlit/WithStreamlitConnection.vue";
export default {
  name: "App",
  components: { ReportFlow, WithStreamlitConnection }
};
</script>

<style>
body {
  margin: 0;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.blinking-dot {
  width: 14px;
  height: 14px;
  background-color: #67C23A;
  border-radius: 50%;
  position: absolute;
  top: 7px;
  right:7px;
  animation: breathe 1.5s infinite;
}

@keyframes breathe {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(0.8);
  }
}
.butterflie-circle-endpoint {
  background: #67C23A !important;
  border: 1px solid #67C23A !important;
}
</style>
