import React, { useState } from "react";
import axios from "axios";

export default function ChatBox() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [...messages, { sender: "user", text: input }];
    setMessages(newMessages);

    try {
      const res = await axios.post("http://127.0.0.1:5000/chat", { question: input });
      const source = res.data.source || "chatgpt";
      const label =
        source === "model" ? "📊 Model" : source === "chatgpt" ? "🤖 ChatGPT" : "🧩 System";

      setMessages([
        ...newMessages,
        { sender: "bot", text: res.data.answer || "No response received.", source, label },
      ]);
    } catch (err) {
      console.error("Chat Error:", err);
      setMessages([
        ...newMessages,
        { sender: "bot", text: "⚠️ Error: Could not connect to backend.", source: "error" },
      ]);
    }

    setInput("");
  };

  return (
    <div style={styles.container}>
      <h2>🔋 Battery SOH Chat Assistant</h2>
      <div style={styles.chatBox}>
        {messages.map((msg, i) => (
          <div key={i} style={msg.sender === "user" ? styles.user : styles.bot}>
            {msg.sender === "bot" && msg.label && (
              <p style={styles.label}>{msg.label}</p>
            )}
            <p>{msg.text}</p>
          </div>
        ))}
      </div>
      <div style={styles.inputRow}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about SOH or battery health..."
        />
        <button onClick={sendMessage} style={styles.button}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { width: "420px", margin: "2rem auto", fontFamily: "Arial" },
  chatBox: {
    border: "1px solid #ccc",
    padding: "10px",
    height: "400px",
    overflowY: "auto",
    marginBottom: "10px",
    background: "#f9f9f9",
    borderRadius: "10px",
  },
  user: {
    textAlign: "right",
    background: "#d1e7dd",
    padding: "8px",
    margin: "5px",
    borderRadius: "10px",
  },
  bot: {
    textAlign: "left",
    background: "#f8d7da",
    padding: "8px",
    margin: "5px",
    borderRadius: "10px",
  },
  label: {
    fontSize: "0.8rem",
    color: "#555",
    marginBottom: "2px",
    fontWeight: "bold",
  },
  inputRow: { display: "flex", gap: "10px" },
  input: { flex: 1, padding: "8px" },
  button: {
    padding: "8px 16px",
    cursor: "pointer",
    backgroundColor: "#007bff",
    color: "white",
    border: "none",
    borderRadius: "5px",
  },
};
