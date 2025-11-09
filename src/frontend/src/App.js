import React from "react";
import Upload from "./Upload";
import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="header">
        <h1>🎥 Suspicious Activity Detection System</h1>
        <p>Upload CCTV or surveillance footage to analyze for anomalies</p>
      </header>

      <Upload />

      <footer className="footer">
        <p>© {new Date().getFullYear()} KIIT University | Developed by Aryan</p>
      </footer>
    </div>
  );
}

export default App;
