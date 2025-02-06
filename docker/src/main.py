import boto3
import pickle
import pandas as pd
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import joblib
from datetime import date, datetime
from decimal import Decimal

s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

S3_BUCKET_NAME = 'modalyze-s3-bucket'
DYNAMODB_TABLE = 'modalyze-table'

def lambda_handler(event, context):
    # Parse S3 event to get file details
    for record in event['Records']:
        s3_key = record['s3']['object']['key']
        user_id = s3_key.split('/')[1]
        file_type = 'model' if 'models' in s3_key else 'validation'

        if file_type == 'model':
            # Wait for validation dataset to be uploaded
            return {"status": "Model uploaded. Waiting for validation dataset."}

        # Download files from S3
        model_path = f"/tmp/model.pkl"  # Temporary Lambda storage
        dataset_path = f"/tmp/validation.csv"
        print(model_path)
        print(dataset_path)
        print(user_id)
        s3_client.download_file(S3_BUCKET_NAME, f"user/{user_id}/models/model.pkl", model_path)
        s3_client.download_file(S3_BUCKET_NAME, f"user/{user_id}/validation_data/validation.csv", dataset_path)
        

        
        # Load model
        with open(model_path, 'rb') as f:
            model = joblib.load(f)
            
        print("Model loaded successfully")
        # Load validation dataset
        df = pd.read_csv(dataset_path)
        X = df.drop('Target', axis=1)  # Replace 'target' with your actual target column name
        y_true = df['Target'].to_numpy()
                
        # Predict and calculate metrics
        y_pred = model.predict(X)
        print("Prediction: ", y_pred)
        metrics = {
            "Mean Squared Error": Decimal(str(mean_squared_error(y_true, y_pred))),
            "Mean Absolute Error": Decimal(str(mean_absolute_error(y_true, y_pred))),
            "R^2 Score": Decimal(str(r2_score(y_true, y_pred))),
        }


        print("Metrics: ", metrics)

        # Save metrics to DynamoDB
        table = dynamodb.Table(DYNAMODB_TABLE)
        table.update_item(
            Key={
                'UserID': user_id,
                'UploadDate': datetime.now().isoformat()
            },
            UpdateExpression="SET #m = :metrics",
            ExpressionAttributeNames={
                "#m": "Metrics"  # Alias for reserved keyword
            },
            ExpressionAttributeValues={
                ":metrics": metrics
            }
        )

        return {
            "statusCode": 200,
            "body": f"Evaluation complete. Metrics: {metrics}"
        }
