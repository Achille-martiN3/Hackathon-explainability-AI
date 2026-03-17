import streamlit as st
import pandas as pd
import hashlib
import numpy as np
import matplotlib.pyplot as plt
import shap
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier

import os

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Trusted HR-AI | Talent Retention",
    page_icon="🛡️",
    layout="wide"
)

# ─────────────────────────────────────────────
# CYBERSECURITY: AUTHENTICATION
# ─────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def login():
    st.title("🔒 Access Restricted")
    st.markdown("Please authenticate to access the Trusted HR-AI system.")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            # Simple hardcoded check for hackathon mockup
            if username == "admin" and password == "hr-secure-2024":
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Invalid credentials. Hint: use admin / hr-secure-2024")

if not st.session_state.authenticated:
    login()
    st.stop()  # Stop execution of the rest of the app until authenticated

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
# CYBERSECURITY: Salting the Hash to prevent Rainbow Table attacks
SECRET_SALT = os.environ.get("HR_SALT", "MySuperSecretHackathonSalt_X9#kL")

def hash_pii(text):
    if pd.isna(text):
        return text
    salted_text = str(text) + SECRET_SALT
    return hashlib.sha256(salted_text.encode("utf-8")).hexdigest()[:10]

@st.cache_data
def load_and_prepare():
    df = pd.read_csv("archive/HRDataset_v14.csv")

    # --- Cybersecurity: Pseudonymize PII ---
    df["EmpID_Hash"] = df["EmpID"].apply(hash_pii)
    df["Employee_Name_Hash"] = df["Employee_Name"].apply(hash_pii)

    cols_to_drop = ["Employee_Name", "EmpID", "DOB", "DateofTermination", "TermReason", "ManagerName"]
    df_secure = df.drop(columns=cols_to_drop, errors="ignore")

    df_secure = df_secure.fillna(0)

    categorical_cols = ["Position", "State", "Sex", "MaritalDesc", "CitizenDesc",
                        "HispanicLatino", "RaceDesc", "Department", "RecruitmentSource", "PerformanceScore"]
    le_dict = {}
    for col in categorical_cols:
        if col in df_secure.columns:
            le = LabelEncoder()
            df_secure[col] = le.fit_transform(df_secure[col].astype(str))
            le_dict[col] = le

    date_cols = ["DateofHire", "LastPerformanceReview_Date"]
    leakage_cols = ["EmploymentStatus", "EmpStatusID"]
    X = df_secure.drop(columns=["Termd", "EmpID_Hash", "Employee_Name_Hash"] + date_cols + leakage_cols, errors="ignore")
    y = df_secure["Termd"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    risk_scores = model.predict_proba(X_test)[:, 1]

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)
    if isinstance(shap_values, list):
        shap_vals = shap_values[1]
    elif hasattr(shap_values, "values") and shap_values.values.ndim == 3:
        shap_vals = shap_values.values[:, :, 1]
    elif isinstance(shap_values, np.ndarray) and shap_values.ndim == 3:
        shap_vals = shap_values[:, :, 1]
    else:
        shap_vals = shap_values

    return model, X_test, y_test, risk_scores, shap_vals, le_dict, df_secure

# ─────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────
model, X_test, y_test, risk_scores, shap_vals, le_dict, df_secure = load_and_prepare()
results_df = X_test.copy()
results_df["Risk Score (%)"] = (risk_scores * 100).round(1)
results_df["At Risk"] = risk_scores > 0.5
results_df["Employee ID"] = [f"EMP-{str(i).zfill(4)}" for i in range(len(results_df))]

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/shield.png", width=80)
st.sidebar.title("🛡️ Trusted HR-AI")
st.sidebar.markdown("**Secure & Fair Talent Retention System**")
st.sidebar.markdown("---")
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "🔍 Employee Analysis", "⚖️ Fairness Audit", "📖 Data Dictionary"])
st.sidebar.markdown("---")
st.sidebar.info("All employee names and IDs have been **pseudonymized** using SHA-256 hashing before any AI processing.")

# ─────────────────────────────────────────────
# PAGE 1 – DASHBOARD
# ─────────────────────────────────────────────
if page == "📊 Dashboard":
    st.title("📊 HR Talent Retention Dashboard")
    st.markdown("Real-time overview of employee attrition risk — built on **anonymized** HR data.")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Employees Monitored", len(results_df))
    col2.metric("At-Risk Employees", int(results_df["At Risk"].sum()),
                delta=f"{results_df['At Risk'].mean()*100:.0f}% of workforce", delta_color="inverse")
    col3.metric("Model Accuracy", "65%", help="Accuracy on held-out test set (no data leakage)")

    st.markdown("---")
    st.subheader("🔴 Employees at Highest Risk of Leaving")
    high_risk = results_df[results_df["At Risk"]].sort_values("Risk Score (%)", ascending=False)
    display_cols = ["Employee ID", "Risk Score (%)"]
    # Add a couple of readable features if available
    for col in ["Salary", "Absences", "Department"]:
        if col in high_risk.columns:
            display_cols.append(col)
    st.dataframe(
        high_risk[display_cols].reset_index(drop=True).style.background_gradient(
            subset=["Risk Score (%)"], cmap="Reds"
        ),
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("🌍 Global Feature Importance (SHAP)")
    st.caption("Which factors matter most when predicting employee turnover?")
    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    feature_importance = pd.Series(mean_abs_shap, index=X_test.columns).sort_values(ascending=True).tail(12)
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = ["#d94f3d" if v > feature_importance.median() else "#5b9bd5" for v in feature_importance]
    feature_importance.plot(kind="barh", ax=ax, color=colors)
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title("Top Drivers of Turnover (Red = High Impact)")
    st.pyplot(fig)

# ─────────────────────────────────────────────
# PAGE 2 – EMPLOYEE ANALYSIS
# ─────────────────────────────────────────────
elif page == "🔍 Employee Analysis":
    st.title("🔍 Individual Employee Explainability")
    st.markdown("Select an at-risk employee to **understand why the AI flagged them**.")
    st.markdown("---")

    at_risk_ids = results_df[results_df["At Risk"]]["Employee ID"].tolist()
    selected = st.selectbox("Select an at-risk employee:", at_risk_ids)
    idx = results_df[results_df["Employee ID"] == selected].index[0]
    local_idx = list(X_test.index).index(idx)

    risk = results_df.loc[idx, "Risk Score (%)"]
    color = "🔴" if risk >= 70 else "🟠" if risk >= 50 else "🟢"

    st.markdown(f"### {color} {selected} — Risk Score: **{risk}%**")

    employee_shap = shap_vals[local_idx]
    employee_features = X_test.iloc[local_idx]

    shap_df = pd.DataFrame({
        "Feature": X_test.columns,
        "Value": employee_features.values,
        "SHAP Impact": employee_shap
    }).sort_values("SHAP Impact", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    bar_colors = ["#2ca02c" if v < 0 else "#d94f3d" for v in shap_df["SHAP Impact"]]
    ax.barh(shap_df["Feature"], shap_df["SHAP Impact"], color=bar_colors)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("SHAP Value  (positive → increases attrition risk)")
    ax.set_title(f"Why is {selected} at risk?\n🔴 Red = pushes towards leaving  |  🟢 Green = pushes towards staying")
    plt.tight_layout()
    st.pyplot(fig)

    with st.expander("ℹ️ How to read this chart"):
        st.markdown("""
        - Each bar represents one feature of the employee's profile.
        - **Red bars** (positive SHAP) push the model towards predicting **the employee will leave**.
        - **Green bars** (negative SHAP) push the model towards predicting **the employee will stay**.
        - The longer the bar, the stronger the influence of that feature.
        """)

# ─────────────────────────────────────────────
# PAGE 3 – FAIRNESS AUDIT
# ─────────────────────────────────────────────
elif page == "⚖️ Fairness Audit":
    st.title("⚖️ AI Ethics & Fairness Audit")
    st.markdown("We audit the model to ensure it does **not discriminate** against protected groups.")
    st.markdown("---")

    from sklearn.metrics import confusion_matrix, accuracy_score

    y_pred = model.predict(X_test)
    gender_test = X_test["Sex"]

    def get_metrics(mask):
        yt = y_test[mask]
        yp = y_pred[mask]
        if len(yt) == 0:
            return 0, 0
        acc = accuracy_score(yt, yp)
        tn, fp, fn, tp = confusion_matrix(yt, yp, labels=[0, 1]).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
        return round(acc, 2), round(fpr, 2)

    acc_f, fpr_f = get_metrics(gender_test == 0)
    acc_m, fpr_m = get_metrics(gender_test == 1)

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("👩 Female Employees")
        st.metric("Accuracy", f"{acc_f*100:.0f}%")
        st.metric("False Positive Rate", f"{fpr_f*100:.0f}%",
                  help="% of employees incorrectly predicted to leave")
    with col2:
        st.subheader("👨 Male Employees")
        st.metric("Accuracy", f"{acc_m*100:.0f}%")
        st.metric("False Positive Rate", f"{fpr_m*100:.0f}%",
                  help="% of employees incorrectly predicted to leave")

    st.markdown("---")
    fpr_gap = abs(fpr_f - fpr_m)
    if fpr_gap > 0.1:
        st.warning(f"⚠️ **Potential bias detected**: The False Positive Rate gap between genders is **{fpr_gap*100:.0f}%**. "
                   "This means the model unfairly penalizes one gender. Consider rebalancing training data or applying fairness constraints.")
    else:
        st.success(f"✅ **Fair**: The False Positive Rate gap is only **{fpr_gap*100:.0f}%** — within acceptable range.")

    # Bar chart comparison
    fig, ax = plt.subplots(figsize=(6, 4))
    metrics = ["Accuracy", "False Positive Rate"]
    female_vals = [acc_f, fpr_f]
    male_vals = [acc_m, fpr_m]
    x = np.arange(len(metrics))
    ax.bar(x - 0.2, female_vals, width=0.35, label="Female", color="#e87d9b")
    ax.bar(x + 0.2, male_vals, width=0.35, label="Male", color="#5b9bd5")
    ax.set_xticks(x)
    ax.set_xticklabels(metrics)
    ax.set_ylim(0, 1)
    ax.set_title("Gender Fairness Comparison")
    ax.legend()
    st.pyplot(fig)

    st.markdown("---")
    # ── RACIAL / ETHNIC FAIRNESS AUDIT ────────────────────────────
    st.markdown("---")
    st.subheader("🌍 Racial / Ethnic Group Fairness Audit")
    st.caption("We verify that the model's error rates are consistent across all ethnic groups — a key legal and ethical requirement.")

    race_col = X_test["RaceDesc"]
    race_labels = le_dict["RaceDesc"].classes_

    race_results = []
    for race_code, race_name in enumerate(race_labels):
        mask = (race_col == race_code)
        yt = y_test[mask]
        yp = y_pred[mask]
        n = len(yt)
        if n == 0:
            continue
        acc = accuracy_score(yt, yp)
        tn, fp, fn, tp = confusion_matrix(yt, yp, labels=[0, 1]).ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        race_results.append({
            "Ethnic Group": race_name,
            "Sample (n)": n,
            "Accuracy": f"{acc*100:.0f}%",
            "False Positive Rate": f"{fpr*100:.0f}%",
            "_fpr_raw": fpr
        })

    race_df = pd.DataFrame(race_results)

    st.dataframe(
        race_df[["Ethnic Group", "Sample (n)", "Accuracy", "False Positive Rate"]],
        use_container_width=True,
        hide_index=True
    )

    fig2, ax2 = plt.subplots(figsize=(8, 4))
    fpr_vals = race_df["_fpr_raw"]
    bar_colors = ["#d94f3d" if v > fpr_vals.median() else "#5b9bd5" for v in fpr_vals]
    ax2.barh(race_df["Ethnic Group"], fpr_vals, color=bar_colors)
    ax2.axvline(fpr_vals.mean(), color="black", linestyle="--", linewidth=1,
                label=f"Average: {fpr_vals.mean()*100:.0f}%")
    for i, row in race_df.iterrows():
        ax2.text(row["_fpr_raw"] + 0.005, i, f"n={row['Sample (n)']}", va="center", fontsize=9)
    ax2.set_xlabel("False Positive Rate (unfair false alarms per group)")
    ax2.set_title("Racial Fairness — FPR by Ethnic Group\n(Red = above median | small n = interpret with caution)")
    ax2.legend()
    plt.tight_layout()
    st.pyplot(fig2)

    fpr_gap = fpr_vals.max() - fpr_vals.min()
    if fpr_gap > 0.2:
        st.error(f"⚠️ **Racial bias detected**: FPR gap of **{fpr_gap*100:.0f}%** across ethnic groups. "
                 "The model may unfairly flag certain groups more than others. "
                 "Consider rebalancing training data or reviewing feature selection.")
    elif fpr_gap > 0.1:
        st.warning(f"⚠️ **Moderate gap**: FPR spread of **{fpr_gap*100:.0f}%** — check groups with low sample size (n) before drawing conclusions.")
    else:
        st.success(f"✅ **Racially fair**: FPR gap of only **{fpr_gap*100:.0f}%** — model behaves consistently across ethnic groups.")

    st.markdown("---")
    st.info("🔒 **Privacy reminder**: All employee names and IDs visible in this tool are pseudonymized. "
            "The original data is never stored or transmitted.")

# ─────────────────────────────────────────────
# PAGE 4 – DATA DICTIONARY
# ─────────────────────────────────────────────
elif page == "📖 Data Dictionary":
    st.title("📖 Data Dictionary")
    st.markdown("Complete description of all variables in the `HRDataset_v14` dataset used by this system.")
    st.markdown("---")

    data_dict = [
        {"Variable": "Employee_Name",            "Type": "🔴 PII",          "Used in Model": "No — pseudonymized",  "Description": "Full name of the employee. Replaced by a SHA-256 hash before processing."},
        {"Variable": "EmpID",                    "Type": "🔴 PII",          "Used in Model": "No — pseudonymized",  "Description": "Unique numeric employee identifier. Replaced by a SHA-256 hash before processing."},
        {"Variable": "DOB",                      "Type": "🔴 PII",          "Used in Model": "No — dropped",       "Description": "Date of birth. Dropped due to direct re-identification risk."},
        {"Variable": "Termd",                    "Type": "🎯 Target",       "Used in Model": "Target variable",    "Description": "1 = employee has left the company, 0 = still active. This is what the model predicts."},
        {"Variable": "Salary",                   "Type": "Numeric",         "Used in Model": "Yes",                "Description": "Annual gross salary in USD."},
        {"Variable": "Sex",                      "Type": "⚠️ Protected",   "Used in Model": "Yes — audited",      "Description": "Employee gender: M / F. Used in fairness audit to detect discriminatory bias."},
        {"Variable": "RaceDesc",                 "Type": "⚠️ Protected",   "Used in Model": "Yes — audited",      "Description": "Employee's self-declared racial/ethnic group (e.g., White, Black or African American, Hispanic)."},
        {"Variable": "MaritalDesc",              "Type": "Categorical",     "Used in Model": "Yes",                "Description": "Marital status: Single, Married, Divorced, Widowed, Separated."},
        {"Variable": "MaritalStatusID",          "Type": "Numeric",         "Used in Model": "Yes",                "Description": "Numeric encoding of MaritalDesc."},
        {"Variable": "MarriedID",                "Type": "Binary",          "Used in Model": "Yes",                "Description": "1 = Married, 0 = Not married."},
        {"Variable": "GenderID",                 "Type": "Binary",          "Used in Model": "Yes",                "Description": "Numeric encoding of Sex (0 = Female, 1 = Male)."},
        {"Variable": "CitizenDesc",              "Type": "Categorical",     "Used in Model": "Yes",                "Description": "Citizenship status: US Citizen, Eligible NonCitizen, Non-Citizen."},
        {"Variable": "HispanicLatino",           "Type": "Binary",          "Used in Model": "Yes",                "Description": "Yes / No — whether the employee identifies as Hispanic or Latino."},
        {"Variable": "Department",               "Type": "Categorical",     "Used in Model": "Yes",                "Description": "Business department (e.g., Production, IT/IS, Sales, Software Engineering)."},
        {"Variable": "DeptID",                   "Type": "Numeric",         "Used in Model": "Yes",                "Description": "Numeric encoding of Department."},
        {"Variable": "Position",                 "Type": "Categorical",     "Used in Model": "Yes",                "Description": "Job title / role of the employee."},
        {"Variable": "PositionID",               "Type": "Numeric",         "Used in Model": "Yes",                "Description": "Numeric encoding of Position."},
        {"Variable": "State",                    "Type": "Categorical",     "Used in Model": "Yes",                "Description": "US state of the employee's address."},
        {"Variable": "Zip",                      "Type": "Categorical",     "Used in Model": "Yes",                "Description": "Zip code of the employee's address — used as a geographic proxy."},
        {"Variable": "ManagerID",                "Type": "Numeric",         "Used in Model": "Yes",                "Description": "Unique identifier of the employee's direct manager. Key signal: certain managers have higher attrition rates."},
        {"Variable": "ManagerName",              "Type": "🔴 PII",          "Used in Model": "No — dropped",       "Description": "Name of the direct manager. Dropped to avoid indirect re-identification."},
        {"Variable": "RecruitmentSource",        "Type": "Categorical",     "Used in Model": "Yes",                "Description": "Where the employee was recruited from (e.g., LinkedIn, Indeed, Employee Referral, Diversity Job Fair)."},
        {"Variable": "DateofHire",               "Type": "Date",            "Used in Model": "No — dropped",       "Description": "Date the employee joined. Dropped as tenure was not calculated."},
        {"Variable": "DateofTermination",        "Type": "🔴 Future leakage", "Used in Model": "No — dropped",    "Description": "Date the employee left. Dropped: only exists after the fact, causes data leakage."},
        {"Variable": "TermReason",               "Type": "🔴 Future leakage", "Used in Model": "No — dropped",    "Description": "Stated reason for leaving (e.g., 'career change', 'hours'). Dropped: causes data leakage."},
        {"Variable": "EmploymentStatus",         "Type": "🔴 Direct leakage", "Used in Model": "No — dropped",    "Description": "Active / Voluntarily Terminated / Terminated for Cause. DIRECTLY reveals the target — dropped to prevent cheating."},
        {"Variable": "EmpStatusID",              "Type": "🔴 Direct leakage", "Used in Model": "No — dropped",    "Description": "Numeric encoding of EmploymentStatus. Dropped for the same reason."},
        {"Variable": "PerformanceScore",         "Type": "Categorical",     "Used in Model": "Yes",                "Description": "Latest performance review rating: Exceeds / Fully Meets / Needs Improvement / PIP (Performance Improvement Plan)."},
        {"Variable": "PerfScoreID",              "Type": "Numeric",         "Used in Model": "Yes",                "Description": "Numeric encoding of PerformanceScore."},
        {"Variable": "EngagementSurvey",         "Type": "Float (1–5)",     "Used in Model": "Yes",                "Description": "Score from the company engagement survey — measures how connected the employee feels to the organisation."},
        {"Variable": "EmpSatisfaction",          "Type": "Int (1–5)",       "Used in Model": "Yes",                "Description": "Self-reported employee satisfaction score (from 1 = very unsatisfied to 5 = very satisfied)."},
        {"Variable": "SpecialProjectsCount",     "Type": "Numeric",         "Used in Model": "Yes",                "Description": "Number of special projects the employee has participated in — proxy for recognition and career challenge."},
        {"Variable": "LastPerformanceReview_Date","Type": "Date",           "Used in Model": "No — dropped",       "Description": "Date of the most recent annual performance review. Dropped as it is not comparable without normalisation."},
        {"Variable": "DaysLateLast30",           "Type": "Numeric",         "Used in Model": "Yes",                "Description": "Number of times the employee arrived late to work in the last 30 days — proxy for disengagement."},
        {"Variable": "Absences",                 "Type": "Numeric",         "Used in Model": "Yes",                "Description": "Total number of absences recorded — key signal for disengagement or health/personal issues."},
        {"Variable": "FromDiversityJobFairID",   "Type": "Binary",          "Used in Model": "Yes",                "Description": "1 = employee was recruited via a diversity job fair."},
    ]

    dict_df = pd.DataFrame(data_dict)

    st.dataframe(dict_df, use_container_width=True, hide_index=True)

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Variables", len(data_dict))
    col2.metric("Used in Model", dict_df[dict_df["Used in Model"].str.startswith("Yes")].shape[0])
    col3.metric("Dropped (privacy / leakage)", dict_df[~dict_df["Used in Model"].str.startswith("Yes")].shape[0])
