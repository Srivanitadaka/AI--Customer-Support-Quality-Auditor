import React, { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [summary, setSummary] = useState("");

  // Handle file selection
  const handleFileUpload = (e) => {
    setFile(e.target.files[0]);
  };

  // Send file to backend
  const getSummary = async () => {
    if (!file) {
      alert("Please upload a TXT file first");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(
        "http://127.0.0.1:5000/summarize",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (data.summary) {
        setSummary(data.summary);
      } else {
        alert("Error: " + data.error);
      }

    } catch (error) {
      alert("Backend connection error");
    }
  };

  return (
    <div style={{ padding: "30px", fontFamily: "Arial" }}>
      <h1>AI Customer Support Auditor</h1>


      {/* File Upload */}
      <input
        type="file"
        accept=".txt"
        onChange={handleFileUpload}
      />

      <br /><br />

      {/* Button */}
      <button onClick={getSummary}>
        Generate Summary
      </button>

      <br /><br />

      {/* Result */}
      {summary && (
        <div>
          <h3>Summary:</h3>
          <p>{summary}</p>
        </div>
      )}
    </div>
  );
}

export default App;


