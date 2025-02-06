# **Modalytics - ML Model Evaluation Platform**

Modalyze is a **machine learning model evaluation platform** that automates model testing and provides performance metrics on AWS. It allows users to upload models and datasets, receive evaluation results, and visualize performance through an interactive dashboard.

---

## **🚀 Features**
- **Auto-Evaluation:** Upload a model and dataset to get performance metrics.
- **AWS Integration:** Uses S3 for model storage, Lambda for execution, and DynamoDB for results.
- **Streamlit Dashboard:** Interactive UI for model uploads, visualizations, and insights.

---

## **🛠️ Tech Stack**
- **Backend:** Python, Docker, AWS DynamoDB
- **Frontend:** Streamlit
- **ML Libraries:** scikit-learn, joblib
- **AWS Services:** S3, Lambda, DynamoDB, CloudWatch, ECR

---


## **⚡ How It Works**

1️⃣ **User uploads a trained ML model** (Pickle/Joblib format) & **validation dataset** (CSV).  

2️⃣ **AWS Lambda fetches the model & dataset from S3** and evaluates it.  

3️⃣ **Predictions are generated**, and **performance metrics (MSE, MAE, R² Score) are stored in DynamoDB**.  

4️⃣ **Results are displayed on the Streamlit dashboard**.  



## **📌 Installation & Setup**

### **1️⃣ Clone the Repository**
```bash
git clone https://github.com/your-username/modalyze.git
cd modalyze
