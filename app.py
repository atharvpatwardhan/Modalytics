import streamlit as st
from user_login import login_user, logout_user
import boto3
import json
from datetime import datetime
import pandas as pd
from boto3.dynamodb.conditions import Key
from decimal import Decimal
import plotly.express as px

# Check login before showing any content
if not login_user():
    st.stop()

AWS_REGION = "us-east-1"
S3_BUCKET_NAME = "modalyze-s3-bucket"
s3_client = boto3.client('s3',
                         aws_access_key_id='your_aws_access_key',
                         aws_secret_access_key='your_aws_secret_access_key',
                         region_name=AWS_REGION)
dynamodb = boto3.resource('dynamodb',
                         aws_access_key_id='your_aws_access_key',
                         aws_secret_access_key='your_aws_secret_access_key',
                        region_name = AWS_REGION)



user_table = dynamodb.Table('modalyze-table')


current_user = st.session_state.username

def fetch_metrics(user_id):
    response = user_table.query(
        KeyConditionExpression=Key('UserID').eq(user_id)
    )

    if 'Item' in response:
        st.write(response['Item'])
    else:
        print("No item found")

    # metrics = response.get('Item', {}).get('Metrics', {})
    # return metrics



def load_users():
    with open("user_data/users.json", "r") as f:
        data = json.load(f)
    return data

#Get history of all models from user
def get_metrics_history(user_id):

    table = dynamodb.Table('modalyze-table')
    response = table.query(
        KeyConditionExpression=Key('UserID').eq(user_id)
    )
    
    # Convert to pandas DataFrame and clean data
    df = pd.DataFrame(response['Items'])
    
    if not df.empty:

        df['UploadDate'] = pd.to_datetime(df['UploadDate'],format='ISO8601', utc=True)
        df = df.sort_values('UploadDate', ascending=False)
        df['Date'] = df['UploadDate'].dt.strftime('%Y-%m-%d %H:%M:%S')

        # Expand metrics dictionary into separate columns  
        metrics_df = pd.json_normalize(df['Metrics'])
        df = pd.concat([df[['UploadDate']], metrics_df], axis=1)
        
        # Convert Decimal to float and dates to datetime
        df = df.applymap(lambda x: float(x) if isinstance(x, Decimal) else x)
        df['UploadDate'] = pd.to_datetime(df['UploadDate'],format='ISO8601',utc=True)

        
    return df


df = get_metrics_history(current_user)

# st.write(df)



st.title("Welcome to Modelytics, " + current_user + "!")

st.title("Model Performance Dashboard")


with st.spinner('Loading metrics history...'):
    df = get_metrics_history(current_user)

if df.empty:
    st.warning("No metrics found for this user")
else:
    # Sort by date
    df = df.sort_values('UploadDate')
    
    st.subheader("Model Metrics Over Time")
    
    # col1, col2, col3 = st.columns(3)
    
    fig = px.line(df, x='UploadDate', y='Mean Squared Error',
                    title='Mean Squared Error')
    st.plotly_chart(fig, use_container_width=True)
    
    fig = px.line(df, x='UploadDate', y='Mean Absolute Error',
                    title='Mean Absolute Error')
    st.plotly_chart(fig, use_container_width=True)
    
    fig = px.line(df, x='UploadDate', y='R^2 Score',
                    title='R² Score', 
                    labels={'R^2 Score': 'R² Score'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Show raw data
    st.subheader("Raw Data")
    st.dataframe(df.style.format({
        'Mean Squared Error': '{:.4f}',
        'Mean Absolute Error': '{:.4f}',
        'R^2 Score': '{:.4f}'
    }))


validation_file = st.file_uploader("Upload Validation Dataset (CSV)", type=["csv","xlsx"])
model_file = st.file_uploader("Upload Trained Model File", type=["pkl", "joblib"])


if validation_file is not None and model_file is not None:
    # When the user clicks the upload button
    if st.button("Upload Files to S3"):
        # Upload validation dataset to S3
        validation_filename = f"user/{current_user}/validation_data/{validation_file.name}"
        s3_client.upload_fileobj(validation_file, S3_BUCKET_NAME, validation_filename)
        
        # Upload model file to S3
        model_filename = f"user/{current_user}/models/{model_file.name}"
        s3_client.upload_fileobj(model_file, S3_BUCKET_NAME, model_filename)
        upload_date = datetime.now().strftime('%Y-%m-%d')


        item = {
            'UserID': current_user,
            'FileID': model_file.name,
            'ModelFilePath': f"s3://{S3_BUCKET_NAME}/{model_filename}",
            'ValidationFilePath': f"s3://{S3_BUCKET_NAME}/{validation_filename}",
            'Metrics': {},  #TODO: Add model metrics here later
            'UploadDate': upload_date
        }

        user_table.put_item(Item=item)


        st.success("Files uploaded successfully!")


if st.button("Fetch Evaluation Metrics"):
    metrics = fetch_metrics(current_user)
    if metrics:
        st.write("Model Evaluation Metrics:")
        st.json(metrics)
    else:
        st.warning("Metrics not yet available. Please check back later.")
