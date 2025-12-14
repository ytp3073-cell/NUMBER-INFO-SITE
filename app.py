from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

# code by abbas
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mobile Tracker Pro - ABBAS</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --primary-color: #6366f1;
            --secondary-color: #8b5cf6;
            --success-color: #10b981;
            --error-color: #ef4444;
            --warning-color: #f59e0b;
            --dark-bg: #111827;
            --light-bg: #f9fafb;
            --dark-card: #1f2937;
            --light-card: #ffffff;
            --dark-text: #f9fafb;
            --light-text: #111827;
            --shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            --shadow-lg: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            color: var(--light-text);
            transition: background 0.3s ease;
        }

        body.dark-mode {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            width: 100%;
        }

        header {
            text-align: center;
            padding: 30px 0;
            position: relative;
        }

        .logo {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 80px;
            height: 80px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            margin-bottom: 20px;
            box-shadow: var(--shadow);
            animation: float 3s ease-in-out infinite;
        }

        @keyframes float {
            0%, 100% { transform: translateY(0); }
            50% { transform: translateY(-10px); }
        }

        .logo i {
            font-size: 36px;
            color: white;
        }

        h1 {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 10px;
            color: white;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }

        .subtitle {
            font-size: 1.1rem;
            color: rgba(255, 255, 255, 0.8);
            margin-bottom: 30px;
        }

        .theme-toggle {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(10px);
            border: none;
            border-radius: 50px;
            padding: 10px 15px;
            cursor: pointer;
            color: white;
            transition: all 0.3s ease;
            box-shadow: var(--shadow);
        }

        .theme-toggle:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.05);
        }

        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            box-shadow: var(--shadow-lg);
            margin-bottom: 30px;
            animation: slideUp 0.5s ease-out;
            transition: all 0.3s ease;
        }

        body.dark-mode .card {
            background: rgba(31, 41, 55, 0.95);
            color: var(--dark-text);
        }

        @keyframes slideUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .input-group {
            position: relative;
            margin-bottom: 25px;
        }

        .input-group input {
            width: 100%;
            padding: 18px 20px 18px 50px;
            background: rgba(255, 255, 255, 0.8);
            border: 2px solid rgba(99, 102, 241, 0.3);
            border-radius: 15px;
            font-size: 18px;
            color: var(--light-text);
            transition: all 0.3s ease;
        }

        body.dark-mode .input-group input {
            background: rgba(31, 41, 55, 0.8);
            color: var(--dark-text);
            border-color: rgba(139, 92, 246, 0.3);
        }

        .input-group input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
            transform: translateY(-2px);
        }

        .input-group i {
            position: absolute;
            left: 20px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--primary-color);
            font-size: 18px;
        }

        .btn {
            width: 100%;
            padding: 18px;
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            border: none;
            border-radius: 15px;
            color: white;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 7px 20px rgba(99, 102, 241, 0.5);
        }

        .btn:active {
            transform: translateY(-1px);
        }

        .btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: 0.5s;
        }

        .btn:hover::before {
            left: 100%;
        }

        .btn i {
            margin-right: 8px;
        }

        .loader-container {
            display: none;
            justify-content: center;
            margin: 30px 0;
        }

        .loader {
            width: 60px;
            height: 60px;
            position: relative;
        }

        .loader-circle {
            position: absolute;
            width: 100%;
            height: 100%;
            border-radius: 50%;
            border: 4px solid rgba(99, 102, 241, 0.2);
            border-top-color: var(--primary-color);
            animation: spin 1.2s linear infinite;
        }

        .loader-text {
            position: absolute;
            top: 70px;
            width: 100%;
            text-align: center;
            font-size: 14px;
            color: var(--primary-color);
            font-weight: 500;
        }

        @keyframes spin {
            100% { transform: rotate(360deg); }
        }

        .message {
            padding: 15px 20px;
            border-radius: 10px;
            margin-top: 20px;
            display: none;
            font-size: 16px;
            animation: slideDown 0.3s ease-out;
        }

        @keyframes slideDown {
            from {
                opacity: 0;
                transform: translateY(-10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        .success-message {
            background: rgba(16, 185, 129, 0.1);
            color: var(--success-color);
            border-left: 4px solid var(--success-color);
        }

        .error-message {
            background: rgba(239, 68, 68, 0.1);
            color: var(--error-color);
            border-left: 4px solid var(--error-color);
        }

        .results-container {
            display: none;
            margin-top: 30px;
            animation: fadeIn 0.5s ease-out;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        .result-header {
            background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
            color: white;
            padding: 20px;
            border-radius: 15px 15px 0 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .result-header h2 {
            font-size: 1.5rem;
            font-weight: 600;
        }

        .result-actions {
            display: flex;
            gap: 10px;
        }

        .action-btn {
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .action-btn:hover {
            background: rgba(255, 255, 255, 0.3);
            transform: scale(1.1);
        }

        .result-body {
            background: white;
            padding: 20px;
            border-radius: 0 0 15px 15px;
            overflow: hidden;
            font-family: monospace;
            white-space: pre-line;
            line-height: 1.6;
        }

        body.dark-mode .result-body {
            background: var(--dark-card);
            color: var(--dark-text);
        }

        .footer {
            text-align: center;
            padding: 30px 0;
            color: rgba(255, 255, 255, 0.8);
            font-size: 14px;
        }

        .footer a {
            color: white;
            text-decoration: none;
            font-weight: 600;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        .history-container {
            margin-top: 30px;
        }

        .history-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .history-header h3 {
            font-size: 1.2rem;
            font-weight: 600;
        }

        .clear-history {
            background: rgba(239, 68, 68, 0.1);
            border: none;
            border-radius: 8px;
            padding: 8px 12px;
            color: var(--error-color);
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .clear-history:hover {
            background: rgba(239, 68, 68, 0.2);
        }

        .history-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .history-item {
            background: rgba(99, 102, 241, 0.1);
            border-radius: 20px;
            padding: 8px 15px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
        }

        .history-item:hover {
            background: rgba(99, 102, 241, 0.2);
            transform: translateY(-2px);
        }

        .history-item i {
            margin-right: 5px;
            font-size: 12px;
        }

        .toast {
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: var(--dark-card);
            color: white;
            padding: 15px 25px;
            border-radius: 10px;
            box-shadow: var(--shadow-lg);
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 1000;
        }

        .toast.show {
            transform: translateX(-50%) translateY(0);
            opacity: 1;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 2rem;
            }
            
            .theme-toggle {
                top: 10px;
                right: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <button class="theme-toggle" id="themeToggle">
                <i class="fas fa-moon" id="themeIcon"></i>
            </button>
            <div class="logo">
                <i class="fas fa-mobile-alt"></i>
            </div>
            <h1>Mobile Tracker Pro</h1>
            <p class="subtitle">Powered by ABBAS</p>
        </header>

        <main>
            <div class="card">
                <div class="input-group">
                    <i class="fas fa-phone"></i>
                    <input type="text" id="number" placeholder="Enter 10 digit mobile number..." maxlength="10">
                </div>

                <button class="btn" id="trackBtn">
                    <i class="fas fa-search"></i> Track Now
                </button>

                <div class="loader-container" id="loaderContainer">
                    <div class="loader">
                        <div class="loader-circle"></div>
                        <div class="loader-text">Tracking...</div>
                    </div>
                </div>
                
                <div id="success" class="message success-message"></div>
                <div id="error" class="message error-message"></div>
            </div>

            <div class="card history-container" id="historyContainer" style="display: none;">
                <div class="history-header">
                    <h3>Recent Searches</h3>
                    <button class="clear-history" id="clearHistory">Clear All</button>
                </div>
                <div class="history-list" id="historyList"></div>
            </div>

            <div class="results-container" id="resultsContainer">
                <div class="result-header">
                    <h2>Tracking Results</h2>
                    <div class="result-actions">
                        <button class="action-btn" id="copyBtn" title="Copy Results">
                            <i class="fas fa-copy"></i>
                        </button>
                        <button class="action-btn" id="shareBtn" title="Share Results">
                            <i class="fas fa-share-alt"></i>
                        </button>
                    </div>
                </div>
                <div class="result-body" id="resultBody"></div>
            </div>
        </main>

        <footer class="footer">
            <p>© 2025 Mobile Tracker Pro | Developed by <a href="#">ABBAS</a></p>
            <p>Join our Telegram: <a href="#">@BAN8T</a></p>
        </footer>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        // Initialize app
        document.addEventListener('DOMContentLoaded', function() {
            // Check for saved theme preference
            const savedTheme = localStorage.getItem('theme');
            if (savedTheme === 'dark') {
                document.body.classList.add('dark-mode');
                document.getElementById('themeIcon').className = 'fas fa-sun';
            }
            
            // Load search history
            loadSearchHistory();
            
            // Event listeners
            document.getElementById('themeToggle').addEventListener('click', toggleTheme);
            document.getElementById('trackBtn').addEventListener('click', startTrack);
            document.getElementById('number').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') startTrack();
            });
            document.getElementById('clearHistory').addEventListener('click', clearSearchHistory);
            document.getElementById('copyBtn').addEventListener('click', copyResults);
            document.getElementById('shareBtn').addEventListener('click', shareResults);
            
            // Auto-format phone number input
            document.getElementById('number').addEventListener('input', function(e) {
                e.target.value = e.target.value.replace(/[^0-9]/g, '').slice(0, 10);
            });
        });

        function toggleTheme() {
            document.body.classList.toggle('dark-mode');
            const isDarkMode = document.body.classList.contains('dark-mode');
            document.getElementById('themeIcon').className = isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        }

        function startTrack() {
            const num = document.getElementById("number").value.trim();
            
            if (num.length !== 10 || isNaN(num)) {
                showError("Please enter a valid 10 digit mobile number");
                return;
            }
            
            // Add to search history
            addToSearchHistory(num);
            
            // Show loader
            document.getElementById("loaderContainer").style.display = "flex";
            document.getElementById("resultsContainer").style.display = "none";
            document.getElementById("error").style.display = "none";
            document.getElementById("success").style.display = "none";
            
            // Disable button during request
            document.getElementById("trackBtn").disabled = true;
            
            fetch('/track?num=' + num)
            .then(res => res.json())
            .then(apiData => {
                // Hide loader
                document.getElementById("loaderContainer").style.display = "none";
                document.getElementById("trackBtn").disabled = false;

                if(apiData.success && apiData.data){
                    showSuccess("Information Found!");
                    displayUserInfo(apiData.data, num);
                }
                else if(apiData.message === "No records found"){
                    showError("❌ No records found for this number.");
                }
                else{
                    showError("❌ No information available.");
                }
            })
            .catch(err => {
                document.getElementById("loaderContainer").style.display = "none";
                document.getElementById("trackBtn").disabled = false;
                showError("Error: " + err.message);
            });
        }

        function displayUserInfo(data, targetNumber) {
            // Format the results in the desired style
            let resultText = `✅ Information Found

🔢 Target Number: ${targetNumber}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📄 Record:
• 👤 Full Name: ${data.name || "N/A"}
• 👨‍🦳 Father Name: ${data.father_name || "N/A"}
• 📱 Mobile Number: ${data.mobile || "N/A"}
• 🆔 Aadhar Number: ${data.id_number || "N/A"}
• 🏠 Complete Address: ${data.address || "N/A"}
• 📞 Alternate Mobile: ${data.alt_mobile || "N/A"}
• 📍 Telecom Circle: ${data.circle || "N/A"}
• 🔢 User ID: ${data.id || "N/A"}

──────────────────────────────

💻 Bot by OGGY BHAI
📱 Join: @BAN8T`;

            document.getElementById("resultBody").innerText = resultText;
            document.getElementById("resultsContainer").style.display = "block";
            
            // Smooth scroll to results
            document.getElementById("resultsContainer").scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }

        function showSuccess(msg) {
            const element = document.getElementById("success");
            element.innerText = msg;
            element.style.display = "block";
            
            // Auto hide after 5 seconds
            setTimeout(() => {
                element.style.display = "none";
            }, 5000);
        }

        function showError(msg) {
            const element = document.getElementById("error");
            element.innerText = msg;
            element.style.display = "block";
            
            // Auto hide after 5 seconds
            setTimeout(() => {
                element.style.display = "none";
            }, 5000);
        }

        function showToast(message) {
            const toast = document.getElementById("toast");
            toast.innerText = message;
            toast.classList.add("show");
            
            setTimeout(() => {
                toast.classList.remove("show");
            }, 3000);
        }

        function copyResults() {
            const resultText = document.getElementById("resultBody").innerText;
            
            navigator.clipboard.writeText(resultText).then(() => {
                showToast("Results copied to clipboard!");
            }).catch(err => {
                showToast("Failed to copy results");
            });
        }

        function shareResults() {
            const resultText = document.getElementById("resultBody").innerText;
            
            if (navigator.share) {
                navigator.share({
                    title: 'Mobile Tracker Results',
                    text: resultText
                }).then(() => {
                    showToast("Results shared successfully!");
                }).catch(err => {
                    showToast("Failed to share results");
                });
            } else {
                // Fallback for browsers that don't support Web Share API
                navigator.clipboard.writeText(resultText).then(() => {
                    showToast("Results copied to clipboard! You can now paste and share.");
                }).catch(err => {
                    showToast("Failed to copy results");
                });
            }
        }

        function loadSearchHistory() {
            const history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
            
            if (history.length > 0) {
                document.getElementById('historyContainer').style.display = 'block';
                renderSearchHistory(history);
            }
        }

        function renderSearchHistory(history) {
            const historyList = document.getElementById('historyList');
            historyList.innerHTML = '';
            
            history.slice(0, 10).forEach(number => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `<i class="fas fa-clock"></i> ${number}`;
                historyItem.addEventListener('click', () => {
                    document.getElementById('number').value = number;
                    startTrack();
                });
                historyList.appendChild(historyItem);
            });
        }

        function addToSearchHistory(number) {
            let history = JSON.parse(localStorage.getItem('searchHistory') || '[]');
            
            // Remove if already exists
            history = history.filter(item => item !== number);
            
            // Add to beginning
            history.unshift(number);
            
            // Keep only last 20 items
            history = history.slice(0, 20);
            
            localStorage.setItem('searchHistory', JSON.stringify(history));
            
            if (history.length > 0) {
                document.getElementById('historyContainer').style.display = 'block';
                renderSearchHistory(history);
            }
        }

        function clearSearchHistory() {
            localStorage.removeItem('searchHistory');
            document.getElementById('historyContainer').style.display = 'none';
            showToast("Search history cleared!");
        }
    </script>
</body>
</html>
'''
#leaked by @BAN8T 
@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/track')
def track():
    num = request.args.get('num')

    if not num or len(num) != 10 or not num.isdigit():
        return jsonify({"success": False, "message": "Invalid mobile number"})

    try:
        api_url = f"https://numapi.anshapi.workers.dev/?num={num}"
        response = requests.get(api_url, timeout=15)
        api = response.json()

        # No record case
        if api.get("success") and isinstance(api.get("result"), dict):
            if api["result"].get("message") == "No records found":
                return jsonify({"success": False, "message": "No records found"})

        # Data present
        if api.get("success") and isinstance(api.get("result"), list):
            return jsonify({"success": True, "data": api["result"][0]})

        return jsonify({"success": False, "message": "Unexpected API response"})

    except Exception as e:
        return jsonify({"success": False, "message": f"Server Error: {str(e)}"})


# Pydroid only
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
#leaked by abbas 

# join @BAN8T 