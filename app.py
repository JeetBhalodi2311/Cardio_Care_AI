import os
import numpy as np
import joblib
import pickle
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Configuration ---
MODEL_PATH = "model1.pkl"

# --- Model Loading ---
model = None

def load_model():
    global model
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            print(f"Model loaded successfully from {MODEL_PATH}")
        except Exception as e_joblib:
            print(f"Joblib load failed: {e_joblib}. Trying pickle...")
            try:
                with open(MODEL_PATH, "rb") as f:
                    model = pickle.load(f)
                print(f"Model loaded successfully using pickle.")
            except Exception as e_pickle:
                print(f"Failed to load model: {e_pickle}")
                model = None
    else:
        print(f"Model file {MODEL_PATH} not found.")

load_model()

# --- Routes ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/disclaimer')
def disclaimer():
    return render_template('disclaimer.html')

@app.route('/predict_ui')
def predict_ui():
    return render_template('predict.html')

@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

@app.route('/accuracy')
def accuracy():
    return render_template('accuracy.html')

def calculate_heart_age(chronological_age, systolic, diastolic, weight, height, cholesterol, gluc, smoke, active):
    heart_age = chronological_age
    
    # BP Impact
    if systolic >= 140 or diastolic >= 90:
        heart_age += 7
    elif systolic >= 130 or diastolic >= 85:
        heart_age += 3
    elif systolic < 120 and diastolic < 80:
        heart_age -= 1
        
    # Smoking Impact
    if smoke == 1:
        heart_age += 5
        
    # BMI Impact
    bmi = weight / ((height / 100) ** 2)
    if bmi >= 30:
        heart_age += 6
    elif bmi >= 25:
        heart_age += 2
        
    # Cholesterol & Glucose
    if cholesterol > 1:
        heart_age += 2
    if gluc > 1:
        heart_age += 2
        
    # Activity
    if active == 0:
        heart_age += 3
    else:
        heart_age -= 1
        
    return round(max(chronological_age - 5, min(heart_age, 100)))

def generate_heart_reboot_plan(data, prediction):
    # Base plan structure
    plan = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    # Extract triggers
    bp_high = float(data.get('ap_hi', 120)) >= 140 or float(data.get('ap_lo', 80)) >= 90
    smoker = int(data.get('smoke', 0)) == 1
    inactive = int(data.get('active', 1)) == 0
    weight = float(data.get('weight', 70))
    height = float(data.get('height', 170))
    bmi = weight / ((height / 100) ** 2)
    obese = bmi >= 30

    # Activity Levels
    base_activity = "15-min light walk" if not inactive else "5-min stretching"
    high_activity = "30-min brisk walk" if not inactive else "15-min modified walk"

    for i, day in enumerate(days):
        day_plan = {"day": day}
        
        # Morning Vital
        if bp_high:
            day_plan["vital"] = "Measure BP (Resting)"
        elif obese:
            day_plan["vital"] = "Record Morning Weight"
        else:
            day_plan["vital"] = "Record Resting Heart Rate"

        # Main Activity Logic
        if i == 0: # Mon
            day_plan["activity"] = base_activity
            day_plan["diet"] = "Cut salt intake by 50%" if bp_high else "Start 2L water goal"
        elif i == 1: # Tue
            day_plan["activity"] = "Isometric wall-sit (30s)" if bp_high else "Light yoga/stretching"
            day_plan["diet"] = "Zero processed sugar today"
        elif i == 2: # Wed
            day_plan["activity"] = high_activity
            day_plan["diet"] = "Add leafy greens to lunch"
        elif i == 3: # Thu
            day_plan["activity"] = "Deep breathing (5 mins)"
            day_plan["diet"] = "Intermittent fasting (12h gap)"
        elif i == 4: # Fri
            day_plan["activity"] = "Bodyweight squats (10 reps)"
            day_plan["diet"] = "Replace caffeine with herbal tea"
        elif i == 5: # Sat
            day_plan["activity"] = "Long nature walk (45 min)"
            day_plan["diet"] = "Try a DASH-diet recipe"
        else: # Sun
            day_plan["activity"] = "Rest & Mobility work"
            day_plan["diet"] = "Meal prep for next week"

        # Special Overlays
        if smoker and i % 2 == 0:
            day_plan["activity"] += " + Lung capacity breaths"
            day_plan["diet"] += " (Nicotine-free window: 4h)"

        plan.append(day_plan)
        
    return plan

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded. Please check server logs.'}), 500

    try:
        data = request.form
        
        age = float(data.get('Age_Year', 45))
        ap_hi = float(data.get('ap_hi', 120))
        ap_lo = float(data.get('ap_lo', 80))
        weight = float(data.get('weight', 70))
        height = float(data.get('height', 170))
        chol = int(data.get('cholesterol', 1))
        gluc = int(data.get('gluc', 1))
        smoke = int(data.get('smoke', 0))
        active = int(data.get('active', 1))

        features = [
            int(data.get('gender', 0)), height, weight, ap_hi, ap_lo, 
            chol, gluc, smoke, int(data.get('alco', 0)), active, age
        ]
        
        # Predict
        prediction = model.predict([features])[0]
        
        # Probability
        probability = 0.0
        if hasattr(model, "predict_proba"):
            prob_array = model.predict_proba([features])[0]
            probability = float(prob_array[1] if len(prob_array) > 1 else prob_array[0]) * 100
        
        # Calculate Heart Age
        heart_age = calculate_heart_age(age, ap_hi, ap_lo, weight, height, chol, gluc, smoke, active)
        
        # Generate 7-Day Reboot Plan
        reboot_plan = generate_heart_reboot_plan(data, int(prediction))

        return jsonify({
            'success': True,
            'prediction': int(prediction), 
            'probability': probability,
            'heart_age': heart_age,
            'chronological_age': age,
            'reboot_plan': reboot_plan
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/generate_report', methods=['POST'])
def generate_report():
    from fpdf import FPDF
    import io
    from datetime import datetime
    from flask import send_file, jsonify

    try:
        data = request.form
        patient_name = data.get('patient_name', 'Valued Patient').strip()
        if not patient_name:
            patient_name = "Valued Patient"
            
        age = float(data.get('Age_Year', 45))
        ap_hi = float(data.get('ap_hi', 120))
        ap_lo = float(data.get('ap_lo', 80))
        weight = float(data.get('weight', 70))
        height = float(data.get('height', 170))
        chol = int(data.get('cholesterol', 1))
        gluc = int(data.get('gluc', 1))
        smoke = int(data.get('smoke', 0))
        active = int(data.get('active', 1))

        features = [
            int(data.get('gender', 0)), height, weight, ap_hi, ap_lo, 
            chol, gluc, smoke, int(data.get('alco', 0)), active, age
        ]
        
        prediction = 0
        probability = 0.0
        if model:
            prediction = int(model.predict([features])[0])
            if hasattr(model, "predict_proba"):
                prob_array = model.predict_proba([features])[0]
                probability = float(prob_array[1] if len(prob_array) > 1 else prob_array[0]) * 100

        heart_age = calculate_heart_age(age, ap_hi, ap_lo, weight, height, chol, gluc, smoke, active)
        bmi = weight / ((height / 100) ** 2)
        reboot_plan = generate_heart_reboot_plan(data, prediction)

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()
        
        # --- Page 1: Clinical Summary ---
        pdf.set_font("Helvetica", 'B', 24)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 20, "Global Heart Passport", ln=True, align='C')
        
        pdf.set_font("Helvetica", '', 10)
        pdf.set_text_color(107, 114, 128)
        pdf.cell(0, 10, f"Issued on: {datetime.now().strftime('%B %d, %Y')} | CardioCare AI Diagnostic", ln=True, align='C')
        
        pdf.ln(10)

        # Patient Info Header
        pdf.set_fill_color(248, 250, 252)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(0, 12, f" PATIENT NAME: {patient_name.upper()}", border=0, ln=True, fill=True)
        pdf.ln(2)
        
        # Risk Summary Header
        pdf.set_fill_color(243, 244, 246)
        pdf.set_font("Helvetica", 'B', 14)
        pdf.set_text_color(31, 41, 55)
        pdf.cell(0, 12, " [1] CLINICAL RISK ASSESSMENT SUMMARY", ln=True, fill=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(45, 10, "Chronological Age :")
        pdf.cell(15, 10, f"{int(age)}")
        pdf.cell(45, 10, "  Functional Heart Age : ")
        
        age_diff = heart_age - age
        if age_diff > 0:
            pdf.set_text_color(220, 38, 38)
            age_text = f"{heart_age} Yrs (+{int(age_diff)})"
        elif age_diff < 0:
            pdf.set_text_color(16, 185, 129)
            age_text = f"{heart_age} Yrs ({int(age_diff)})"
        else:
            pdf.set_text_color(37, 99, 235)
            age_text = f"{heart_age} Yrs (Optimal)"
            
        pdf.cell(0, 10, age_text, ln=True)
        pdf.set_text_color(31, 41, 55)
        
        risk_status = "HIGH RISK" if prediction == 1 else "LOW RISK"
        status_color = (220, 38, 38) if prediction == 1 else (16, 185, 129)
        
        pdf.cell(45, 10, "Risk Status : ")
        pdf.set_text_color(*status_color)
        pdf.cell(40, 10, risk_status)
        pdf.set_text_color(31, 41, 55)
        pdf.cell(30, 10, "   Probability : ")
        pdf.cell(0, 10, f"{probability:.2f}%", ln=True)
        
        pdf.ln(5)
        pdf.set_font("Helvetica", 'B', 12)
        pdf.cell(0, 10, f"Vital Parameters for {patient_name}:", ln=True)
        pdf.set_font("Helvetica", '', 10)
        
        def add_row(label, value, unit=""):
            pdf.set_fill_color(252, 252, 252)
            pdf.cell(60, 8, f" {label}", border=1, fill=True)
            pdf.cell(0, 8, f" {value} {unit}", border=1, ln=True)

        add_row("Height", height, "cm")
        add_row("Weight", weight, "kg")
        add_row("BMI", f"{bmi:.2f}", "kg/m2")
        add_row("Blood Pressure", f"{ap_hi}/{ap_lo}", "mmHg")
        add_row("Cholesterol", ["Normal", "Above Normal", "High"][chol-1])
        add_row("Glucose", ["Normal", "Above Normal", "High"][gluc-1])
        
        pdf.ln(10)
        pdf.set_fill_color(243, 244, 246)
        pdf.set_font("Helvetica", 'B', 14)
        pdf.cell(0, 12, " [1] AI-DRIVEN PERSONALIZED HEALTH ADVICE", ln=True, fill=True)
        pdf.ln(5)
        
        pdf.set_font("Helvetica", '', 10)
        if prediction == 1 or age_diff > 5:
            pdf.set_text_color(185, 28, 28)
            pdf.multi_cell(0, 7, f"CRITICAL INSIGHT for {patient_name}: Your Heart Age is {heart_age}, which is {int(age_diff) if age_diff > 0 else 'significantly'} years older than your actual age. This indicates rapid cardiovascular aging.")
            pdf.set_text_color(31, 41, 55)
            pdf.ln(2)
            pdf.multi_cell(0, 7, "- Priority 1: Consult a cardiologist to discuss preventative medication.\n- Priority 2: Adopt a DASH diet and reduce daily salt below 1,500mg.\n- Priority 3: Begin daily aerobic activity (light walking) to 'de-age' your heart.")
        else:
            pdf.set_text_color(15, 118, 110)
            pdf.multi_cell(0, 7, f"HEALTH OPTIMIZATION for {patient_name}: Your heart is aging at a healthy rate. Maintaining current status is key.")
            pdf.set_text_color(31, 41, 55)
            pdf.ln(2)
            pdf.multi_cell(0, 7, "- Focus on longevity through strength training and high-fiber intake.\n- Avoid any new tobacco exposure which could accelerate heart aging by 5-10 years.")

        pdf.ln(10)
        pdf.set_font("Helvetica", 'I', 8)
        pdf.set_text_color(107, 114, 128)
        pdf.multi_cell(0, 5, "DISCLAIMER: This report is AI-generated for educational purposes only. It is not a clinical diagnosis.")

        # --- Page 2: 7-Day Heart Reboot Blueprint ---
        pdf.add_page()
        pdf.set_font("Helvetica", 'B', 20)
        pdf.set_text_color(37, 99, 235)
        pdf.cell(0, 15, " [2] 7-DAY HEART REBOOT BLUEPRINT", ln=True, align='L')
        pdf.set_font("Helvetica", '', 10)
        pdf.set_text_color(75, 85, 99)
        pdf.multi_cell(0, 6, f"Tailored action plan for {patient_name} based on current clinical risk profile. Follow these daily steps to optimize cardiovascular performance.")
        pdf.ln(5)

        # Using fpdf2 table feature for perfect alignment
        table_data = [
            ("Day", "Morning Vital", "Activity Goal", "Dietary Focus")
        ]
        for day in reboot_plan:
            table_data.append((
                day['day'],
                day['vital'],
                day['activity'],
                day['diet']
            ))

        with pdf.table(
            borders_layout="SINGLE_TOP_LINE",
            cell_fill_color=(250, 250, 252),
            cell_fill_mode="ROWS",
            line_height=8,
            text_align=("LEFT", "LEFT", "LEFT", "LEFT"),
            width=190,
            col_widths=(25, 40, 60, 65)
        ) as table:
            for i, row in enumerate(table_data):
                row_cells = table.row()
                if i == 0:
                    pdf.set_font("Helvetica", 'B', 10)
                    pdf.set_text_color(255, 255, 255)
                    pdf.set_fill_color(37, 99, 235)
                else:
                    pdf.set_font("Helvetica", '', 9)
                    pdf.set_text_color(31, 41, 55)
                    pdf.set_fill_color(250, 250, 252) if i % 2 == 0 else pdf.set_fill_color(255, 255, 255)
                    
                for cell_text in row:
                    row_cells.cell(cell_text)

        pdf.ln(10)
        pdf.set_font("Helvetica", 'B', 11)
        pdf.set_text_color(15, 118, 110)
        pdf.cell(0, 10, "Pro Tip: Consistency is better than intensity. Start small, stay steady.", ln=True)

        # In fpdf2, output() returns bytearray by default
        pdf_bytes = pdf.output()
        
        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)
        
        # Format filename
        safe_name = patient_name.replace(" ", "_").lower()
        filename = f"{safe_name}_Heart_Passport_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"PDF GENERATION ERROR: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/chat', methods=['POST'])
def chat():
    import random
    data = request.json
    user_msg = data.get('message', '').lower().strip()
    
    # Advanced prioritized responses with expanded details
    medical_responses = {
        "symptom": "Warning symptoms of heart trouble include: 1. Chest pain or pressure, 2. Shortness of breath, 3. Pain in neck/jaw/back, 4. Nausea or cold sweats, 5. Lightheadedness. If these occur suddenly, call emergency services immediately (102 or your local number).",
        "chest pain": "Chest pain (Angina) can feel like squeezing, pressure, or fullness. While it can be non-cardiac (like GERD), it is often the first sign of a heart attack. Do not ignore it – seek immediate medical evaluation at an ER.",
        "systolic": "Systolic pressure (the top/higher number) measures the force your heart exerts on artery walls during a beat. Normal is < 120. Elevated is 120-129. Stage 1 Hypertension is 130-139. High systolic pressure is a major risk factor for stroke and heart disease.",
        "diastolic": "Diastolic pressure (the bottom/lower number) measures the force between beats while the heart rests. Normal is < 80. Consistent readings above 80 indicate hypertension. Both numbers are critical for your heart health assessment.",
        "bmi": "Body Mass Index (BMI) categories: Underweight (<18.5), Normal (18.5-24.9), Overweight (25-29.9), and Obese (30+). A higher BMI increases the workload on your heart and raises the risk of diabetes and high blood pressure.",
        "cholesterol": "Cholesterol has two main types: LDL ('bad') which clogs arteries, and HDL ('good') which clears them. To lower LDL: avoid trans fats, eat more soluble fiber (oats, beans), and consume Omega-3s (salmon, walnuts).",
        "exercise": "The goal is at least 150 minutes of moderate aerobic activity (like brisk walking) or 75 minutes of vigorous activity (running/swimming) per week, plus muscle-strengthening exercises twice a week. Start slow and stay consistent!",
        "diet": "A heart-healthy diet focuses on: 1. Fruits/Vegetables (half your plate), 2. Whole grains, 3. Lean proteins (fish, poultry, legumes), 4. Limiting salt, sugar, and saturated fats. The DASH and Mediterranean diets are excellent benchmarks.",
        "smoke": "Smoking is a leading cause of cardiovascular disease. It damages the lining of your arteries, leads to plaque buildup, and reduces oxygen in your blood. Quitting at any age significantly lowers heart attack risk within 1-2 years.",
        "pressure": "Hypertension (High Blood Pressure) is often called the 'silent killer' because it has no symptoms but causes permanent damage to the heart, brain, and kidneys. Reducing salt and increasing exercise are the best non-medical ways to lower it.",
        "salt": "High sodium intake causes the body to retain water, raising blood pressure. Aim for less than 2,300mg/day (about 1 teaspoon). Avoid processed foods, canned soups, and salty snacks to protect your arteries.",
        "prevention": "Top 5 Preventive Steps: 1. Know your numbers (BP, Cholesterol, Glucose), 2. Move your body daily, 3. Eat real, unprocessed food, 4. Manage stress through sleep/medication, 5. Avoid all tobacco products.",
        "doctor": "Our Specialists page lists experts who can provide personalized care. If your Assessment shows High Risk, we recommend booking a consultation immediately for a professional diagnostic workup.",
        "heart attack": "Signs of a heart attack: Chest discomfort, upper body pain (arms, back, neck), stomach pain (sometimes mistaken for indigestion), and shortness of breath. Time is heart muscle – seek help instantly.",
        "stroke": "Use the FAST acronym for Stroke: Face drooping, Arm weakness, Speech difficulty, Time to call emergency services. Strokes are often caused by the same risk factors as heart disease, like high BP.",
        "weight": "Losing even 5-10% of your body weight can dramatically improve your blood pressure and cholesterol levels, reducing the strain on your cardiovascular system.",
        "diabetes": "High blood sugar damages blood vessels and the nerves that control your heart. Managing your 'A1C' levels is crucial for preventing long-term cardiovascular complications.",
        "alcohol": "Excessive alcohol can raise blood pressure and contribute to heart failure. If you drink, limit it to 1 drink/day for women and 2/day for men.",
        "stress": "Chronic stress increases hormones like cortisol, which can raise BP and heart rate. Practice deep breathing, meditation, or regular physical activity to help manage stress levels."
    }

    # Group 2: Medium Priority (Greetings/General)
    general_responses = {
        "hello": "Hello! I'm Hearty, your AI specialist. I can explain your test results, give diet/exercise advice, or help you understand symptoms. What's on your mind?",
        "hi": "Hi there! Ready to take control of your heart health? Ask me about things like blood pressure, BMI, or healthy eating!",
        "hey": "Hey! How can I help you stay healthy today? I have lots of information on heart disease prevention and lifestyle tips.",
        "who are you": "I'm Hearty AI, a dedicated cardiovascular health assistant. I use clinical guidelines to help users understand their heart risks and live longer, healthier lives.",
        "thanks": "You're welcome! My goal is to see you stay healthy. Don't forget to check your 'Assessment' results!",
        "thank you": "It's my pleasure! I'm here 24/7 if you have more questions about your heart. Stay active!",
        "help": "I can help with: 1. Explaining BP/BMI numbers, 2. Diet and Exercise tips, 3. Identifying heart attack signs, 4. Finding a doctor. What specifically do you need?",
        "ok": "Great! Let me know if you have any specific questions about your heart health or our services.",
        "good": "Wonderful! Keeping a positive attitude is actually good for your heart too. Anything else I can help with?"
    }

    # Custom multi-keyword search logic
    response = None
    
    # 1. Check Medical (Priority) - Matches if any word is in message
    for key, value in medical_responses.items():
        if key in user_msg:
            response = value
            break
            
    # 2. Check General (If no medical match)
    if not response:
        for key, value in general_responses.items():
            if key in user_msg:
                response = value
                break
                
    # 3. Randomized Fallback
    if not response:
        fallbacks = [
            "That's a good question! To give you the best advice, could you ask me about specific things like 'Blood Pressure', 'Diet', 'Smoking', or 'Symptoms'?",
            "I'm not sure I understand that perfectly. However, I can tell you all about how to prevent heart disease if you're interested!",
            "I recommend checking our 'Specialists' page for an expert opinion. Would you like to know more about the different heart symptoms I recognize?",
            "I'm still learning! You can try asking: 'What are heart attack signs?' or 'How much should I exercise?'",
            "I'm here to help with your cardio health! Try mentioning keywords like 'cholesterol', 'bmi', or 'salt intake'."
        ]
        response = random.choice(fallbacks)

    return jsonify({'response': response})

# <<<<<<< HEAD
# # if __name__ == '__main__':
# #     app.run(debug=True, port=8080)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

