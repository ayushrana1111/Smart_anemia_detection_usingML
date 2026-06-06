import streamlit as st
import pandas as pd
import hashlib
import os
import pickle
import matplotlib.pyplot as plt
from PIL import Image

st.title("Smart Anemia Detection System")

st.markdown("---")
st.markdown("**Developed by Group 22 (Ashish kumar, Ayush Rana, Afroj Ahmad) | B.Tech CSE | 2026**")

USER_FILE = "users.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USER_FILE):
        return pd.DataFrame(columns=["username", "password", "approved"])
    return pd.read_csv(USER_FILE)

def user_exists(username):
    users = load_users()
    return username in users["username"].values

def register_user(username, password):
    users = load_users()
    hashed_password = hash_password(password)
    new_user = pd.DataFrame([[username, hashed_password, "no"]], columns=["username", "password", "approved"])
    users = pd.concat([users, new_user], ignore_index=True)
    users.to_csv(USER_FILE, index=False)
    st.success("✅ Registration successful! Wait for admin approval.")

def authenticate(username, password):
    if username == "ayush" and password == "ayush19":
        return True
    users = load_users()
    hashed_password = hash_password(password)
    if user_exists(username):
        user_data = users[users["username"] == username].iloc[0]
        if user_data["password"] == hashed_password:
            if user_data["approved"] == "yes":
                return True
            else:
                st.error("⏳ Waiting for admin approval.")
                return False
    st.error("🚫 Invalid username or password!")
    return False

def login():
    st.title("🔒 Secure Login")
    username = st.text_input("👤 Username:")
    password = st.text_input("🔑 Password:", type="password")
    if "login_attempt" not in st.session_state:
        st.session_state.login_attempt = False
    if st.button("Login"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.login_attempt = True
            st.success(f"✅ Welcome, {username}!")
    if st.session_state.login_attempt:
        st.session_state.login_attempt = False
        st.rerun()

def register():
    st.title("📝 Register New Account")
    username = st.text_input("Create Username:")
    password = st.text_input("Create Password:", type="password")
    confirm_password = st.text_input("Confirm Password:", type="password")
    if st.button("Register"):
        if password == confirm_password:
            if not user_exists(username):
                register_user(username, password)
            else:
                st.error("🚨 Username already taken!")
        else:
            st.error("❌ Passwords do not match!")

def admin_approve_users():
    st.title("🔑 Admin Approval Panel")
    users = load_users()
    if users.empty:
        st.warning("⚠️ No users found!")
        return
    pending_users = users[users["approved"] == "no"]
    if not pending_users.empty:
        st.write("🚀 Pending User Approvals:")
        for index, row in pending_users.iterrows():
            if st.button(f"✅ Approve {row['username']}", key=row['username']):
                users.loc[users["username"] == row["username"], "approved"] = "yes"
                users.to_csv(USER_FILE, index=False)
                st.success(f"User '{row['username']}' approved!")
                st.rerun()
    else:
        st.success("✅ No pending approvals!")

def logout():
    st.session_state.logged_in = False

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    page = st.sidebar.radio("Select", ["Login", "Register"])
    if page == "Login":
        login()
    elif page == "Register":
        register()
else:
    st.sidebar.button("🔓 Logout", on_click=logout)

    if st.session_state.username == "megha":
        admin_approve_users()

    def home_page():
        st.markdown("<h2>🔬🩸 Anemia Shield: Detect & Prevent</h2>", unsafe_allow_html=True)
        st.subheader("Your Smart Health Companion for Anemia Diagnosis")
        try:
            img = Image.open(r"anemia.webp").resize((620, 400))
            st.image(img, use_container_width=500)
        except Exception as e:
            st.error(f"Error loading image: {e}")
        st.markdown("""
        ### 🚀 What You Can Do Here:
        - ✅ **Instant Anemia Diagnosis** based on WHO guidelines.
        - 💊 **Personalized Preventive Measures** to improve your health.
        - 📊 **Data Visualization & Insights** on anemia severity and trends.
        - 🔍 **Easy-to-Use & AI-Powered** for accurate results.
        """, unsafe_allow_html=True)
        st.subheader("🩺 Start Your Anemia Diagnosis Now! 🩺")

    def diagnosis_page():
        with open(r"anemia_detector (1).pkl", "rb") as model_file:
            model = pickle.load(model_file)

        category_map = {"Male": 0, "Female": 1, "Child": 2, "Pregnant Woman": 3}

        def classify_anemia(hemoglobin, category):
            anemia_ranges = {
                "Male":           [(13.0, float("inf"), "Normal"), (11.0, 12.9, "Mild Anemia"), (8.0, 10.9, "Moderate Anemia"), (0, 7.9, "Severe Anemia")],
                "Female":         [(12.0, float("inf"), "Normal"), (11.0, 11.9, "Mild Anemia"), (8.0, 10.9, "Moderate Anemia"), (0, 7.9, "Severe Anemia")],
                "Child":          [(11.0, float("inf"), "Normal"), (10.0, 10.9, "Mild Anemia"), (7.0, 9.9, "Moderate Anemia"), (0, 6.9, "Severe Anemia")],
                "Pregnant Woman": [(11.0, float("inf"), "Normal"), (10.0, 10.9, "Mild Anemia"), (7.0, 9.9, "Moderate Anemia"), (0, 6.9, "Severe Anemia")]
            }
            for lower, upper, severity in anemia_ranges.get(category, []):
                if lower <= hemoglobin <= upper:
                    return severity
            return "Unknown"

        def classify_anemia_type(hemoglobin, mch, mchc, mcv):
            if hemoglobin >= 12.0:
                return "No Anemia", "✅ Your blood parameters are within normal range."
            if mcv < 80:
                if mchc < 32:
                    return "Iron Deficiency Anemia", (
                        "🔴 Your red blood cells are small and pale — classic sign of iron deficiency.\n"
                        "💊 Allopathy: Ferrous Sulfate 325mg daily, Vitamin C for absorption.\n"
                        "🌿 Ayurveda: Punarnava Mandur, dates with jaggery, pomegranate juice.\n"
                        "🍃 Diet: Spinach, lentils, red meat, beetroot, sesame seeds.\n"
                        "⚠️ Avoid tea/coffee after meals — they block iron absorption."
                    )
                else:
                    return "Thalassemia (Possible)", (
                        "🟠 Small red blood cells with normal/high MCHC — may indicate Thalassemia.\n"
                        "💊 Consult a hematologist for Hb electrophoresis confirmation.\n"
                        "🌿 Ayurveda: Ashwagandha, Guduchi for general strength.\n"
                        "🍃 Diet: High protein foods, folate-rich vegetables.\n"
                        "⚠️ Do NOT self-supplement iron — it can be harmful in Thalassemia."
                    )
            elif mcv > 100:
                if mch > 32:
                    return "Vitamin B12 / Folate Deficiency Anemia", (
                        "🔵 Your red blood cells are abnormally large — caused by B12 or Folate deficiency.\n"
                        "💊 Allopathy: Cyanocobalamin (B12) injections or oral supplements, Folic Acid 5mg.\n"
                        "🌿 Ayurveda: Brahmi, Ashwagandha for neurological support.\n"
                        "🍃 Diet: Eggs, dairy, fish, leafy greens, fortified cereals.\n"
                        "⚠️ Strictly avoid alcohol — it depletes B12 and Folate rapidly."
                    )
                else:
                    return "Macrocytic Anemia (Mixed cause)", (
                        "🔵 Large red blood cells detected. Could be B12, Folate, liver, or thyroid related.\n"
                        "💊 Consult a doctor for full blood panel — B12, Folate, TFT, LFT.\n"
                        "🌿 Ayurveda: Triphala churna, Brahmi for liver and nerve support.\n"
                        "🍃 Diet: Eggs, legumes, fortified grains, green vegetables.\n"
                        "⚠️ Do not self-diagnose — get tested before supplementing."
                    )
            else:
                if mchc < 32:
                    return "Anemia of Chronic Disease", (
                        "🟡 Normal-sized but fewer red blood cells — often linked to chronic illness.\n"
                        "💊 Treat the underlying condition. Doctor may prescribe Erythropoietin.\n"
                        "🌿 Ayurveda: Draksharishta tonic, Shilajit for energy and immunity.\n"
                        "🍃 Diet: Anti-inflammatory foods — turmeric, ginger, omega-3 rich fish.\n"
                        "⚠️ Monitor kidneys and inflammation markers with regular blood tests."
                    )
                else:
                    return "Hemolytic / Blood Loss Anemia (Possible)", (
                        "🟠 Normal cell size but low hemoglobin — red blood cells may be breaking down.\n"
                        "💊 Seek immediate medical evaluation. May need Folic Acid + specialist care.\n"
                        "🌿 Ayurveda: Guduchi, Manjistha for blood purification.\n"
                        "🍃 Diet: Iron-rich and antioxidant foods — berries, leafy greens, nuts.\n"
                        "⚠️ This type requires urgent diagnosis — do not delay medical consultation."
                    )

        preventive_measures = {
            "Normal": "✅ Maintain a balanced diet rich in iron, vitamin B12, and folic acid.\n✅ Stay hydrated and get regular checkups.\n✅ Exercise to improve circulation and oxygen transport.\n💊 Allopathy: Not required, but Ferrous Sulfate (325mg) can be taken if needed.\n🌿 Ayurveda: Chyawanprash daily and Triphala churna for better iron absorption.\n🍃 Naturopathy: Beetroot & carrot juice, morning sun exposure for Vitamin D.\n🏡 Homeopathy: Ferrum Phosphoricum 6X, a mild iron supplement.",
            "Mild Anemia": "⚠️ Increase intake of iron-rich foods (spinach, lentils, red meat).\n⚠️ Take vitamin C-rich foods (oranges, lemons, amla) to enhance iron absorption.\n⚠️ Avoid tea/coffee immediately after meals.\n💊 Allopathy: Ferrous Sulfate tablets, Vitamin C supplements.\n🌿 Ayurveda: Ashwagandha, Guduchi, and dates with jaggery.\n🍃 Naturopathy: Pomegranate or wheatgrass juice, deep breathing exercises.\n🏡 Homeopathy: Natrum Muriaticum 30C.",
            "Moderate Anemia": "⚠️ Consult a doctor for further evaluation.\n⚠️ Include iron, vitamin B12, and folate supplements if recommended.\n⚠️ Avoid excessive alcohol consumption.\n💊 Allopathy: Ferrous Fumarate, Folic Acid, Vitamin B12 injections.\n🌿 Ayurveda: Punarnava Mandur tablets, Pomegranate juice daily.\n🍃 Naturopathy: Green smoothies (spinach, kale, moringa), nettle leaf tea.\n🏡 Homeopathy: China Officinalis 30C.",
            "Severe Anemia": "🚨 Seek immediate medical attention.\n🚨 You may need specialized treatment like transfusions or medications.\n🚨 Maintain a high-protein, iron-rich diet with doctor supervision.\n💊 Allopathy: Iron Sucrose IV infusion, Erythropoietin injections.\n🌿 Ayurveda: Draksharishta (grape-based iron tonic), Mandoor Bhasma.\n🍃 Naturopathy: Fresh Aloe Vera juice, Beetroot juice therapy.\n🏡 Homeopathy: Ferrum Metallicum 30C."
        }

        st.markdown("### 🩸 Patient Information")
        col1, col2 = st.columns(2)
        with col1:
            name     = st.text_input("Enter your name:")
            age      = st.number_input("Enter your age:", min_value=1, max_value=120, step=1)
            category = st.selectbox("Select Category:", ["Male", "Female", "Child", "Pregnant Woman"])
            weight   = st.number_input("Enter your weight (kg):", min_value=10.0, max_value=200.0, step=0.1)

        with col2:
            st.markdown("### 🔬 Blood Test Parameters")
            hemoglobin = st.number_input("Hemoglobin - Hb (g/dL):", min_value=1.0, max_value=20.0, step=0.1, value=13.0,
                                         help="Normal: Male 13-17, Female 12-15, Child 11-16 g/dL")
            mch        = st.number_input("MCH (pg):", min_value=10.0, max_value=45.0, step=0.1, value=27.0,
                                         help="Mean Corpuscular Hemoglobin. Normal range: 27–33 pg")
            mchc       = st.number_input("MCHC (g/dL):", min_value=20.0, max_value=40.0, step=0.1, value=32.0,
                                         help="Mean Corpuscular Hemoglobin Concentration. Normal: 32–36 g/dL")
            mcv        = st.number_input("MCV (fL):", min_value=50.0, max_value=130.0, step=0.1, value=85.0,
                                         help="Mean Corpuscular Volume. Normal range: 80–100 fL")

        with st.expander("📖 Where do I find these values? (Click to expand)"):
            st.markdown("""
            These values are found in a standard **CBC (Complete Blood Count)** blood test report:
            | Parameter | Full Name | Normal Range |
            |-----------|-----------|--------------|
            | **Hb** | Hemoglobin | Male: 13–17 g/dL, Female: 12–15 g/dL |
            | **MCH** | Mean Corpuscular Hemoglobin | 27–33 pg |
            | **MCHC** | Mean Corpuscular Hemoglobin Concentration | 32–36 g/dL |
            | **MCV** | Mean Corpuscular Volume | 80–100 fL |
            """)

        if st.button("🔍 Detect Anemia", use_container_width=True):
            severity   = classify_anemia(hemoglobin, category)
            prevention = preventive_measures.get(severity, "No recommendations available.")
            anemia_type, type_advice = classify_anemia_type(hemoglobin, mch, mchc, mcv)

            try:
                category_encoded = category_map[category]
                ml_input = [[age, weight, category_encoded, hemoglobin]]
                ml_prediction = model.predict(ml_input)[0]
                ml_result = ml_prediction
            except Exception:
                ml_result = "N/A"

            st.markdown("---")
            st.markdown("## 📋 Diagnosis Report")

            col1, col2, col3 = st.columns(3)
            col1.metric("Severity", severity)
            col2.metric("Anemia Type", anemia_type)
            col3.metric("ML Prediction", ml_result)

            st.markdown(f"""
            **Patient:** {name} | **Age:** {age} | **Category:** {category} | **Weight:** {weight} kg

            | Parameter | Your Value | Normal Range |
            |-----------|-----------|--------------|
            | Hemoglobin (Hb) | {hemoglobin} g/dL | Male ≥13, Female ≥12 |
            | MCH | {mch} pg | 27–33 pg |
            | MCHC | {mchc} g/dL | 32–36 g/dL |
            | MCV | {mcv} fL | 80–100 fL |
            """)

            st.markdown("### 🔬 Anemia Type Analysis")
            st.info(f"**Detected Type:** {anemia_type}")
            for line in type_advice.split("\n"):
                st.write(line)

            st.markdown("### 🩺 General Preventive Measures")
            for line in prevention.split("\n"):
                st.write(line)

            st.success("✅ Patient data saved successfully!")

            patient_data = pd.DataFrame(
                [[name, age, weight, category, hemoglobin, mch, mchc, mcv, severity, anemia_type, ml_result]],
                columns=["Name", "Age", "Weight", "Category", "Hb Level", "MCH", "MCHC", "MCV",
                         "Anemia Severity", "Anemia Type", "ML Prediction"]
            )
            if os.path.exists("anemia_patient_data.csv"):
                patient_data.to_csv("anemia_patient_data.csv", mode='a', header=False, index=False)
            else:
                patient_data.to_csv("anemia_patient_data.csv", index=False)

    def patient_data_page():
        st.markdown("<h2>📋 Patient Diagnosis Records</h2>", unsafe_allow_html=True)
        try:
            df = pd.read_csv("anemia_patient_data.csv")
            st.dataframe(df)
        except FileNotFoundError:
            st.warning("⚠️ No patient records found. Diagnose a patient to see data here!")

    def visualization_page():
        st.markdown("<h2 style='text-align: center;'>📊 Anemia Data Visualization</h2>", unsafe_allow_html=True)
        try:
            df = pd.read_csv("anemia_patient_data.csv").dropna(subset=["Anemia Severity"])

            # Chart 1: Pie Chart
            st.markdown("### 🥧 Anemia Severity Distribution")
            anemia_counts = df["Anemia Severity"].value_counts()
            fig1, ax1 = plt.subplots(figsize=(6, 6))
            ax1.pie(anemia_counts, labels=anemia_counts.index, autopct="%1.1f%%",
                    colors=["#66b3ff", "#ff9999", "#ffcc99", "#99ff99"], startangle=90)
            ax1.set_title("Severity Distribution", fontsize=14, fontweight="bold")
            st.pyplot(fig1)

            st.markdown("---")

            # Chart 2: Bar Chart by Category
            st.markdown("### 📊 Anemia Cases by Patient Category")
            category_counts = df["Category"].value_counts()
            fig2, ax2 = plt.subplots(figsize=(8, 5))
            bars = ax2.bar(category_counts.index, category_counts.values,
                           color=["#4e79a7", "#f28e2b", "#e15759", "#76b7b2"])
            ax2.set_xlabel("Patient Category", fontsize=12)
            ax2.set_ylabel("Number of Patients", fontsize=12)
            ax2.set_title("Patients by Category", fontsize=14, fontweight="bold")
            for bar in bars:
                ax2.text(bar.get_x() + bar.get_width() / 2,
                         bar.get_height() + 0.1,
                         str(int(bar.get_height())),
                         ha="center", va="bottom", fontsize=11, fontweight="bold")
            st.pyplot(fig2)

            st.markdown("---")

            # Chart 3: Anemia Type Horizontal Bar
            st.markdown("### 🔬 Anemia Type Distribution")
            if "Anemia Type" in df.columns:
                type_counts = df["Anemia Type"].value_counts()
                fig3, ax3 = plt.subplots(figsize=(9, 5))
                bars3 = ax3.barh(type_counts.index, type_counts.values,
                                 color=["#e15759", "#4e79a7", "#f28e2b",
                                        "#76b7b2", "#59a14f", "#edc948"])
                ax3.set_xlabel("Number of Patients", fontsize=12)
                ax3.set_title("Distribution of Anemia Types", fontsize=14, fontweight="bold")
                for bar in bars3:
                    ax3.text(bar.get_width() + 0.05,
                             bar.get_y() + bar.get_height() / 2,
                             str(int(bar.get_width())),
                             ha="left", va="center", fontsize=11, fontweight="bold")
                st.pyplot(fig3)

            st.markdown("---")

            # Chart 4: Hemoglobin Histogram
            st.markdown("### 🩸 Hemoglobin Level Distribution")
            fig4, ax4 = plt.subplots(figsize=(8, 5))
            ax4.hist(df["Hb Level"], bins=15, color="#e15759", edgecolor="white", linewidth=0.8)
            ax4.axvline(x=12, color="#4e79a7", linestyle="--", linewidth=2, label="Female Normal (12 g/dL)")
            ax4.axvline(x=13, color="#f28e2b", linestyle="--", linewidth=2, label="Male Normal (13 g/dL)")
            ax4.set_xlabel("Hemoglobin Level (g/dL)", fontsize=12)
            ax4.set_ylabel("Number of Patients", fontsize=12)
            ax4.set_title("Hemoglobin Level Distribution", fontsize=14, fontweight="bold")
            ax4.legend()
            st.pyplot(fig4)

            st.markdown("---")

            # Summary Stats
            st.markdown("### 📋 Quick Summary")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Patients", len(df))
            col2.metric("Avg Hemoglobin", f"{df['Hb Level'].mean():.1f} g/dL")
            col3.metric("Most Common", anemia_counts.index[0])
            col4.metric("Severe Cases", len(df[df["Anemia Severity"] == "Severe Anemia"]))

            if st.button("🔄 Refresh Charts"):
                st.rerun()

        except FileNotFoundError:
            st.error("❌ No data available for visualization. Diagnose some patients first!")

    PAGES = {
        "Home": home_page,
        "Diagnosis": diagnosis_page,
        "Patient Data": patient_data_page,
        "Visualization": visualization_page
    }

    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", list(PAGES.keys()))
    PAGES[page]()
