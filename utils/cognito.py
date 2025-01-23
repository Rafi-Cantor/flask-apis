import boto3
import hmac
import hashlib
import base64
import settings


cognito_client = boto3.client('cognito-idp', region_name=settings.COGNITO_REGION)


def get_secret_hash(username: str):
    message = username + settings.COGNITO_APP_CLIENT_ID
    dig = hmac.new(
        bytearray(settings.COGNITO_CLIENT_SECRET, "utf-8"), msg=message.encode("UTF-8"), digestmod=hashlib.sha256
    ).digest()
    secret_hash = base64.b64encode(dig).decode()
    return secret_hash
