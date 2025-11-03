# Flask is the micro web framework for Python to define routes (APIs), 
# request read data send from the frontend like a JSON input
# jsonify converts Python dictionaries into JSON format to send back as a response
from flask import Flask, request, jsonify

# CORS allows cross-origin request, so my React frontend can call the API
from flask_cors import CORS

# numpy is for numerical computation which turns input data into NumPy arrays
import numpy as np

# pickle is used to laod pre-trained ML model (battery_soh_model.pkl)
import pickle
import os

# load_dotenv reads my .env file to load sensitive keys such as the OpenAI key
from dotenv import load_dotenv

# to access the ChatGPT API
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client 
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Will test connection to verify the API key is working, if sucessful, prints confirmation, if not shows error message
try:
    client.models.list()
    print("✅ OpenAI API connection successful")
except Exception as e:
    print("❌ API connection error:", e)

# Setup Flask app, enables CORS so that your React frontend can make request without being blocked
app = Flask(__name__)
CORS(app)

# Load ML Model, builds the absolute path to your trained ML file
model_path = os.path.join(os.path.dirname(__file__), "battery_soh_model.pkl")

# Will check if the model file exist
if not os.path.exists(model_path):
    print("⚠️ Model file not found. Train it using Linear_Regression.py first.")
    model = None
else:
    model = pickle.load(open(model_path, "rb"))
    print("✅ Model loaded successfully.")

# Variables to store the latest prediction
latest_soh_value = None
latest_status = None

# Defines a root route that returns simple JSON message
# Used for  testing if API is up and running
@app.route("/")
def home():
    return jsonify({"message": "Battery SOH API is running!"})


# Create a route to handle POST requests
@app.route("/predict", methods=["POST"])
def predict_soh():
    global latest_soh_value, latest_status
   
# Reads the JSON body sent by the frontend
    try:
        data = request.get_json()
        u_values = data.get("u_values", [])

# Validates input, must have exactly 21 features, if not will return HTTP 400, a bad request
        if not u_values or len(u_values) != 21:
            return jsonify({"error": "Expected 21 U-values"}), 400

        # Run model prediction
        input_data = np.array(u_values).reshape(1, -1)
        soh_pred = model.predict(input_data)[0] if model else 0.0

        # Example metrics & random feature importance
        metrics = {"R²": 0.95, "MSE": 0.002, "MAE": 0.01}
        importance = {f"U{i+1}": round(np.random.random(), 3) for i in range(5)}

        # Determine health status
        status = "Healthy" if soh_pred > 0.7 else "Unhealthy"

        # 🔹 Save latest values for chatbot use
        latest_soh_value = soh_pred
        latest_status = status

        # Send prediction result to frontend
        return jsonify({
            "soh": float(soh_pred),
            "status": status,
            "metrics": metrics,
            "importance": importance
        })

# Handles any runtime errors gracefully and returns a 500 Internal Server Error
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Chat Endpoint (uses OpenAI + local model)
@app.route("/chat", methods=["POST"])
def chat():
    global latest_soh_value, latest_status
    try:
        data = request.get_json()
        question = data.get("question", "").lower()

        # Local query: user asks for battery SOH
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

        # General queries → send to GPT
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
    
# Handles unexpected chat error gracefully
    except Exception as e:
        print("❌ Error in /chat:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
