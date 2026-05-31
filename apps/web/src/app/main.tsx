import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "app/shared/i18n";
import { App } from "./App";
import "./styles.css";

const root = document.getElementById("root");
if (root === null) {
  throw new Error('Missing root element "#root"');
}

createRoot(root).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
