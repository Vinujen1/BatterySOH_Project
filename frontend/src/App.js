import React, { useState } from "react";
import axios from "axios";
import "./index.css";
import { API_URL } from "./config";

function App() {
  const [uValues, setUValues] = useState(Array(21).fill(3.5));
  const [soh, setSoh] = useState(null);
  const [status, setStatus] = useState("");
  const [metrics, setMetrics] = useState({});
  const [importance, setImportance] = useState({});
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [mode, setMode] = useState("general");

  const predictSOH = async () => {
    try {
      const res = await axios.post(`${API_URL}/predict`, { u_values: uValues });
      setSoh(res.data.soh.toFixed(3));
      setStatus(res.data.status);
      setMetrics(res.data.metrics);
      setImportance(res.data.importance);
    } catch (err) {
      console.error(err);
    }
  };

  const askChat = async () => {
    try {
    const res = await axios.post(`${API_URL}/chat`, { question, mode });      
    setAnswer(res.data.answer);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-slate-100 p-8">
      <h1 className="text-3xl md:text-4xl font-bold text-gray-800 mb-10 flex items-center gap-2">
        <span role="img" aria-label="battery">🔋</span> Battery Health Dashboard
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
        {/* -------- Left Section (Inputs & Predictions) -------- */}
        <div className="bg-white/80 backdrop-blur-md shadow-lg rounded-2xl p-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">
            Input Voltages (U1–U21)
          </h2>

          <div className="grid grid-cols-3 sm:grid-cols-5 gap-2 mb-4">
            {uValues.map((v, i) => (
              <input
                key={i}
                type="number"
                step="0.01"
                className="w-full border border-gray-300 rounded-md text-center p-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-400"
                value={v}
                onChange={(e) => {
                  const copy = [...uValues];
                  copy[i] = parseFloat(e.target.value);
                  setUValues(copy);
                }}
              />
            ))}
          </div>

          <button
            onClick={predictSOH}
            className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-2 rounded-lg transition-colors duration-200"
          >
            Predict SOH
          </button>

          {soh && (
            <div className="mt-6 bg-blue-50 p-4 rounded-lg border border-blue-100">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">Predicted SOH:</h3>
              <p className="text-2xl font-bold text-blue-700">{soh}</p>
              <p className={`mt-1 ${status === "Healthy" ? "text-green-600" : "text-red-600"}`}>
                {status === "Healthy" ? "✅ Healthy" : "⚠️ Unhealthy"}
              </p>
              <progress value={soh} max="1" className="w-full mt-3 h-3"></progress>
            </div>
          )}

          <div className="mt-6">
            <h3 className="font-semibold text-gray-700 flex items-center gap-2">
              📊 Model Metrics
            </h3>
            {Object.keys(metrics).length ? (
              Object.entries(metrics).map(([k, v]) => (
                <p key={k} className="text-sm text-gray-600">{k}: {v}</p>
              ))
            ) : (
              <p className="text-sm text-gray-400">No metrics available yet.</p>
            )}
          </div>

          <div className="mt-4">
            <h3 className="font-semibold text-gray-700 flex items-center gap-2">
              🔥 Top Feature Importances
            </h3>
            {Object.keys(importance).length ? (
              Object.entries(importance).map(([k, v]) => (
                <p key={k} className="text-sm text-gray-600">{k}: {v.toFixed(5)}</p>
              ))
            ) : (
              <p className="text-sm text-gray-400">No importance data yet.</p>
            )}
          </div>
        </div>

        {/* -------- Right Section (Chatbot) -------- */}
        <div className="bg-white/80 backdrop-blur-md shadow-lg rounded-2xl p-6 border border-gray-100">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
            💬 Chatbot Assistant
          </h2>

          <div className="flex gap-2 mb-3">
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="border border-gray-300 rounded-md p-2 text-sm"
            >
              <option value="general">General Knowledge</option>
              <option value="explain">Explain Prediction</option>
            </select>
            <input
              type="text"
              placeholder="Ask a question..."
              className="flex-1 border border-gray-300 rounded-md p-2 text-sm focus:ring-2 focus:ring-blue-400"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
            />
            <button
              onClick={askChat}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm transition-colors"
            >
              Ask
            </button>
          </div>

          <div className="border rounded-md bg-gray-50 p-4 text-gray-700 min-h-[120px]">
            {answer ? <p>{answer}</p> : <p className="text-gray-400">Type a question and click Ask.</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
