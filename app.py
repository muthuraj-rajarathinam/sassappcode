from flask import Flask, Response, render_template_string, request, jsonify
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
import random
import time
import threading

app = Flask(__name__)

# --- METRICS ---
REQUEST_COUNT = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"])
REQUEST_LATENCY = Histogram("http_request_duration_seconds", "Request latency (seconds)", ["endpoint"])
RANDOM_GAUGE = Gauge("random_value", "Random value gauge")
USERS_SIGNED_UP = Counter("users_signed_up_total", "Total users signed up")

# --- ROUTES ---
@app.route("/")
def home():
    REQUEST_COUNT.labels(request.method, "/", 200).inc()
    REQUEST_LATENCY.labels("/").observe(random.uniform(0.05, 0.2))
    return render_template_string(HOME_HTML)

@app.route("/signup", methods=["POST"])
def signup():
    REQUEST_COUNT.labels(request.method, "/signup", 201).inc()
    REQUEST_LATENCY.labels("/signup").observe(random.uniform(0.1, 0.3))
    USERS_SIGNED_UP.inc()
    return jsonify({"status": "success", "message": "Welcome to the platform!"}), 201

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

# --- UI TEMPLATE (SaaS Style Landing Page) ---
HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>🚀 CloudMetrics - Modern SaaS Tool</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { font-family: 'Segoe UI', sans-serif; }
    .hero { min-height: 90vh; display: flex; align-items: center; justify-content: center;
            background: linear-gradient(135deg, #4f46e5, #06b6d4); color: white; }
    .hero h1 { font-size: 3rem; font-weight: 700; }
    .feature-card { border-radius: 15px; transition: 0.3s; }
    .feature-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.15); }
  </style>
</head>
<body>

  <!-- Hero Section -->
  <section class="hero text-center">
    <div>
      <h1>CloudMetrics</h1>
      <p class="lead">A modern SaaS demo app with built-in monitoring</p>
      <button class="btn btn-light btn-lg" onclick="signup()">🚀 Get Started</button>
    </div>
  </section>

  <!-- Features -->
  <section class="container py-5">
    <div class="row text-center">
      <div class="col-md-4">
        <div class="p-4 feature-card bg-light">
          <h3>⚡ Fast API</h3>
          <p>Experience blazing fast performance with optimized APIs.</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="p-4 feature-card bg-light">
          <h3>📊 Built-in Metrics</h3>
          <p>Monitor everything in Prometheus & visualize in Grafana.</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="p-4 feature-card bg-light">
          <h3>🔒 Secure</h3>
          <p>Enterprise-grade security baked into every layer.</p>
        </div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="text-center py-3 bg-dark text-light">
    <p>© 2025 CloudMetrics - Demo SaaS with Monitoring</p>
  </footer>

  <script>
    function signup() {
      fetch('/signup', {method: 'POST'}).then(r => r.json()).then(data => alert(data.message));
    }
  </script>
</body>
</html>
"""

# --- BACKGROUND JOB ---
def background_task():
    while True:
        RANDOM_GAUGE.set(random.uniform(50, 150))
        time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=background_task, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)

