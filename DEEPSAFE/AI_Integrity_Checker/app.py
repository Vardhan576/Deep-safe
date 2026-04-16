import os
from functools import wraps
from flask import Flask, request, render_template, jsonify, send_file, session, redirect, url_for, flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

from database import init_db, log_scan, get_recent_scans, create_user, get_user_by_username
from utils.text_extractor import extract_text
from utils.ai_detector import calculate_ai_percentage, calculate_media_ai_percentage, advanced_media_analysis
from utils.cyber_analyzer import full_analysis
from utils.ctf_generator import build_ctf_challenge
from utils.steg_analyzer import advanced_steganalysis

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = os.environ.get('SECRET_KEY', 'super-secret-key-deep-safe') # Set a secret key for sessions
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not password:
            flash('Username and password are required', 'error')
        elif password != confirm_password:
            flash('Passwords do not match', 'error')
        else:
            hashed_pw = generate_password_hash(password)
            if create_user(username, hashed_pw):
                flash('Account created successfully. Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Username already exists', 'error')
                
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/steganography')
@login_required
def steganography_page():
    return render_template('steganography.html')

@app.route('/cyber-analyzer')
@login_required
def cyber_analyzer_page():
    return render_template('cyber_analyzer.html')

@app.route('/advanced-analyzer')
@login_required
def advanced_analyzer_page():
    return render_template('advanced_analyzer.html')

@app.route('/api/cyber-analyze', methods=['POST'])
def cyber_analyze():
    data = request.get_json(silent=True)
    if not data or 'text' not in data:
        return jsonify({"success": False, "error": "No text provided."}), 400
    text = data['text'].strip()
    if not text:
        return jsonify({"success": False, "error": "Input text is empty."}), 400
    try:
        result = full_analysis(text)
        result['success'] = True
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/history', methods=['GET'])
def history():
    scans = get_recent_scans()
    return jsonify({"success": True, "scans": scans})

@app.route('/api/detect-ai', methods=['POST'])
def detect_ai():
    if 'document' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
        
    file = request.files['document']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            ext = os.path.splitext(filename)[1].lower()
            text_exts = ['.txt', '.pdf', '.docx']
            
            if ext in text_exts:
                text = extract_text(filepath)
                if not text.strip():
                    return jsonify({"success": False, "error": "Could not extract any text from the document."}), 400
                ai_percentage = calculate_ai_percentage(text)
                total_words = len(text.split())
            else:
                filesize = os.path.getsize(filepath)
                ai_percentage = calculate_media_ai_percentage(filename, filesize)
                total_words = "N/A (Media)"
                
            log_scan(filename, ai_percentage)
            
            return jsonify({
                "success": True, 
                "filename": filename,
                "ai_percentage": ai_percentage,
                "total_words": total_words
            })
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            if os.path.exists(filepath):
                try: os.remove(filepath)
                except: pass

@app.route('/api/media-analyze', methods=['POST'])
def media_analyze():
    if 'document' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
        
    file = request.files['document']
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            ext = os.path.splitext(filename)[1].lower()
            text_exts = ['.txt', '.pdf', '.docx']
            text = ""
            if ext in text_exts:
                text = extract_text(filepath)
            
            filesize = os.path.getsize(filepath)
            result = advanced_media_analysis(filename, filesize, text)
            return jsonify(result)
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 500
        finally:
            if os.path.exists(filepath):
                try: os.remove(filepath)
                except: pass

DELIMITER = b"||DEEPVERIFY_STEG||"

@app.route('/api/stegano/encode', methods=['POST'])
def stegano_encode():
    if 'image' not in request.files or 'secret_text' not in request.form:
        return jsonify({"success": False, "error": "Missing file or secret text"}), 400
        
    file = request.files['image']
    secret_text = request.form['secret_text']
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if file and secret_text:
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        output_filename = f"encoded_{filename}"
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], output_filename)
        
        file.save(input_path)
        
        try:
            with open(input_path, 'rb') as f:
                file_bytes = f.read()
                
            with open(output_path, 'wb') as f:
                f.write(file_bytes)
                f.write(DELIMITER)
                f.write(secret_text.encode('utf-8'))
            
            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return jsonify({"success": False, "error": f"Encoding failed: {str(e)}"}), 500
        finally:
            if os.path.exists(input_path):
                try: os.remove(input_path)
                except: pass

@app.route('/api/stegano/decode', methods=['POST'])
def stegano_decode():
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
        
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        try:
            with open(input_path, 'rb') as f:
                content = f.read()
                
            if DELIMITER in content:
                secret_text_bytes = content.split(DELIMITER)[-1]
                secret_text = secret_text_bytes.decode('utf-8', errors='ignore')
                return jsonify({"success": True, "secret_text": secret_text})
            else:
                 return jsonify({"success": False, "error": "No hidden message found in this file."}), 400
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to reveal data. Details: {str(e)}"}), 500
        finally:
            if os.path.exists(input_path):
                try: os.remove(input_path)
                except: pass

@app.route('/api/stegano/advanced-analyze', methods=['POST'])
def advanced_stegano_analyze():
    if 'image' not in request.files:
        return jsonify({"success": False, "error": "No file uploaded"}), 400
        
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({"success": False, "error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(file.filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        try:
            result = advanced_steganalysis(input_path)
            return jsonify({"success": True, "analysis": result})
        except Exception as e:
            return jsonify({"success": False, "error": f"Failed to analyze data. Details: {str(e)}"}), 500
        finally:
            if os.path.exists(input_path):
                try: os.remove(input_path)
                except: pass

@app.route('/api/generate-ctf', methods=['POST'])
@login_required
def generate_ctf():
    data = request.get_json(silent=True) or {}
    category = data.get('category', 'Cryptography')
    difficulty = data.get('difficulty', 'Medium')
    
    try:
        result = build_ctf_challenge(category, difficulty)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
