# Trusted HR-AI: Secure & Fair Talent Retention Assistant

## 1. Overview

Problem statement: 
How can we harness sensitive HR data to retain top talent, **without** risking discriminatory biases or exposing the company to privacy and security vulnerabilities?

This project proposes a Trusted HR-AI assistant that:
- Predicts which employees are at risk of leaving.
- Explains the reason (key factors behind the risk).
- Respects cybersecurity, privacy (GDPR), and ethical AI principles.

We focused on two main themes:
- AI & Cybersecurity
- AI Ethics (Fairness & Non-discrimination)

---

## 2. Objectives

Business objectives:
- Identify key drivers of employee turnover using HR data.
- Flag at-risk employees early so HR can take preventive actions.
- Provide transparent explanations that HR can understand and trust.

Trust & responsibility objectives
- Protect sensitive HR data from leaks, misuse, and attacks.
- Avoid discriminatory outcomes against protected groups (e.g., gender, ethnicity, age).
- Ensure the model is auditable, explainable, and compliant** with GDPR and AI Act principles.

---

## 3. Project Roadmap

### Stage 1: Data Preparation & Cybersecurity (Privacy by Design)
- **Goal**: Protect sensitive PII (Personally Identifiable Information) before any data touches the ML model.
- **Actions**:
  - Load the `HRDataset_v14.csv`.
  - Cryptographically hash identifiers (`EmpID` and `Employee_Name`) using **SHA-256**.
  - Drop highly identifying features (`DOB`) and data leakage variables (`DateofTermination`, `TermReason`).

### Stage 2: AI Model Training
- **Goal**: Build a supervised learning model to predict employee turnover (`Termd` variable).
- **Actions**:
  - Preprocess data (impute missing values, encode categoricals).
  - Train an interpretable base model (e.g., **Random Forest**).
  - Evaluate standard performance metrics (Accuracy, F1-Score).

### Stage 3: Ethics & Fairness 
- **Goal**: Ensure the AI does not discriminate against protected groups (e.g., gender, race).
- **Actions**:
  - Evaluate the model's False Positive / False Negative rates specifically across protected attributes like `Sex` and `RaceDesc`.
  - Utilize tools like `Fairlearn` to measure and potentially mitigate disparate impact.

### Stage 4: Explainability (XAI)
- **Goal**: Avoid a "black box" system by explaining *why* the AI made a prediction.
- **Actions**:
  - Implement **SHAP (SHapley Additive exPlanations)**.
  - Visualize the individual impact of each feature (e.g., low `Salary` vs low `SpecialProjectsCount`) on an employee's risk score.

### Stage 5: User Interface (Demo)
- **Goal**: Provide an actionable, secure dashboard for HR professionals.
- **Actions**:
  - Build a web application using **Streamlit**.
  - The HR user logs in, views a dashboard of safely anonymized employee IDs, and can click on "at-risk" employees to see their specific SHAP explainability charts.

### Stage 6: Deliverables & Documentation
- **Actions**:
  - Complete this **README** and the Technical Documentation.
  - Draw the **Architecture Scheme**.
  - Fill out the **Data Card** and **Model Card** (.docx).
  - Prepare the final Pitch and PowerPoint slides for the 15-minute defense.

---
