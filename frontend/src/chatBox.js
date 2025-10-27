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
      setMessages([...newMessages, { sender: "bot", text: res.data.answer || "No response received." }]);
    } catch (err) {
      console.error("Chat Error:", err);
      setMessages([...newMessages, { sender: "bot", text: "⚠️ Error: Could not connect to backend." }]);
    }

    setInput("");
  };

  return (
    <div style={styles.container}>
      <h2>🔋 Battery SOH Chat Assistant</h2>
      <div style={styles.chatBox}>
        {messages.map((msg, i) => (
          <div key={i} style={msg.sender === "user" ? styles.user : styles.bot}>
            {msg.text}
          </div>
        ))}
      </div>
      <div style={styles.inputRow}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about SOH or dataset..."
        />
        <button onClick={sendMessage} style={styles.button}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { width: "400px", margin: "2rem auto", fontFamily: "Arial" },
  chatBox: {
    border: "1px solid #ccc",
    padding: "10px",
    height: "400px",
    overflowY: "auto",
    marginBottom: "10px",
    background: "#f9f9f9",
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
  inputRow: { display: "flex", gap: "10px" },
  input: { flex: 1, padding: "8px" },
  button: { padding: "8px 16px", cursor: "pointer" },
};
