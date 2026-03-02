import React, { useState } from "react";
import "./App.css";

function App() {

  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {

    if (!file) {
      alert("Please upload a file");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("http://127.0.0.1:5000/analyze", {
      method: "POST",
      body: formData
    });

    const data = await response.json();
    setResult(data);
  };

  return (
    <div className="App">
      <h2>Customer Support QA Auditor</h2>

      <input type="file" onChange={handleFileChange} />
      <br /><br />

      <button onClick={handleUpload}>Analyze</button>

      {result && (
        <div className="result">
          <h3>Analysis Result</h3>

          <p><b>Summary:</b> {result.conversation_summary}</p>
          <p><b>Sentiment:</b> {result.customer_sentiment}</p>
          <p><b>Agent Performance:</b> {result.agent_performance}</p>
          <p><b>Issue Category:</b> {result.issue_category}</p>
          <p><b>Resolution Status:</b> {result.resolution_status}</p>
        </div>
      )}
    </div>
  );
}

export default App;
