from dotenv import load_dotenv
import os

load_dotenv()
COGNITO_REGION = os.environ["COGNITO_REGION"]
COGNITO_USER_POOL_ID = os.environ["COGNITO_USER_POOL_ID"]
COGNITO_APP_CLIENT_ID = os.environ["COGNITO_APP_CLIENT_ID"]
COGNITO_CLIENT_SECRET = os.environ["COGNITO_CLIENT_SECRET"]

DB_ENDPOINT = os.environ["DB_ENDPOINT"]
DB_USER_NAME = os.environ["DB_USER_NAME"]
DB_NAME = os.environ["DB_NAME"]
DB_PASSWORD = os.environ["DB_PASSWORD"]
