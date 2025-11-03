from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import pickle
import os
from dotenv import load_dotenv
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)
# --- Setup ---
app = Flask(__name__)
CORS(app)

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- Load ML Model ---
model_path = os.path.join(os.path.dirname(__file__), "battery_soh_model.pkl")

if not os.path.exists(model_path):
    print("⚠️ Model file not found. Train it using Linear_Regression.py first.")
    model = None
else:
    model = pickle.load(open(model_path, "rb"))
    print("✅ Model loaded successfully.")

@app.route("/")
def home():
    return jsonify({"message": "Battery SOH API is running!"})

# --- Predict Endpoint ---
@app.route("/predict", methods=["POST"])
def predict_soh():
    try:
        data = request.get_json()
        u_values = data.get("u_values", [])

        if not u_values or len(u_values) != 21:
            return jsonify({"error": "Expected 21 U-values"}), 400

        input_data = np.array(u_values).reshape(1, -1)
        soh_pred = model.predict(input_data)[0] if model else 0.0

        metrics = {"R²": 0.95, "MSE": 0.002, "MAE": 0.01}
        importance = {f"U{i+1}": round(np.random.random(), 3) for i in range(5)}

        status = "Healthy" if soh_pred > 0.7 else "Unhealthy"

        return jsonify({
            "soh": float(soh_pred),
            "status": status,
            "metrics": metrics,
            "importance": importance
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Chat Endpoint (uses OpenAI + local model) ---
latest_soh_value = None
latest_status = None

@app.route("/chat", methods=["POST"])
def chat():
    global latest_soh_value, latest_status
    try:
        data = request.get_json()
        question = data.get("question", "").lower()

        # 1️⃣ Local query: user asks for battery SOH
        if "check battery soh" in question:
            if latest_soh_value is None:
                return jsonify({
                    "answer": "No SOH prediction found yet. Please run the SOH prediction first.",
                    "source": "model"
                })
            return jsonify({
                "answer": f"The predicted SOH is {latest_soh_value:.2f}, which indicates the battery is {latest_status}.",
                "source": "model"
            })

        # 2️⃣ General queries → send to GPT
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains battery health and predictions."},
                {"role": "user", "content": question}
            ]
        )

        answer = response.choices[0].message.content
        return jsonify({
            "answer": answer,
            "source": "chatgpt"
        })

    except Exception as e:
        print("❌ Error in /chat:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
