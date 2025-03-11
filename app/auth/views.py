import flask
from flask import request, jsonify
from app.auth import auth
import flask_httpauth
from botocore.exceptions import ClientError
from utils import cognito
import settings
from objects import user
import jwt
from jwt import PyJWTError, PyJWKClient

token_auth = flask_httpauth.HTTPTokenAuth("token")
basic_auth = flask_httpauth.HTTPBasicAuth()
multi_auth = flask_httpauth.MultiAuth(basic_auth, token_auth)


@basic_auth.verify_password
def verify_password(email, password):
    try:
        secret_hash = cognito.get_secret_hash(email)
        cognito.cognito_client.admin_initiate_auth(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password,
                'SECRET_HASH': secret_hash
            },
        )
        logged_in_user = user.User.from_email(email)
        return logged_in_user
    except ClientError:
        return False


@token_auth.verify_token
def verify_token(token):
    try:
        jwks_url = f'https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/' \
                   f'{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json'
        jwk_client = PyJWKClient(jwks_url)
        signing_key = jwk_client.get_signing_key_from_jwt(token)
        decoded_token = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.COGNITO_APP_CLIENT_ID,
            issuer=f'https://cognito-idp.{settings.COGNITO_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}',
            options={"verify_aud": False}
        )
        user_cognito_id = decoded_token.get("sub")
        logged_in_user = user.User.from_cognito_id(user_cognito_id)
        return logged_in_user
    except PyJWTError:
        return False


@auth.route('/register', methods=["POST"])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error_message': 'Email and password are required.'}), 400
    secret_hash = cognito.get_secret_hash(email)
    try:
        new_user = cognito.cognito_client.sign_up(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            Username=email,
            Password=password,
            SecretHash=secret_hash,
        )
    except ClientError as e:
        return jsonify({'error_message': f"Cannot register user with {email}. Reason: {str(e.args)}"}), 500
    else:
        try:
            user.User.create(cognito_id=new_user["UserSub"], email=email)
        except user.CannotCreateNewUserError as e:
            return jsonify({'error_message': f"Cannot register user with {email}. Reason: {str(e.args)}"}), 500

    return jsonify({'message': f"User with {email} has been created"}), 201


@auth.route('/confirm_account', methods=["POST"])
def confirm_account():
    data = request.get_json()
    confirmation_code = data.get('code')
    email = data.get('email')
    if not email or not confirmation_code:
        return jsonify({'error_message': 'Email and confirmation_code are required.'}), 400

    verify_user = user.User.from_email(email=email)

    try:
        secret_hash = cognito.get_secret_hash(email)
        cognito.cognito_client.confirm_sign_up(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            SecretHash=secret_hash,
            Username=email,
            ConfirmationCode=confirmation_code
        )
    except ClientError as e:
        return jsonify({'error_message': f"Cannot confirm account with {email}. Reason: {str(e.args)}"}), 500
    else:
        try:
            verify_user.verify_email(verify_user.user_id)
        except user.CannotVerifyEmailError as e:
            return jsonify({'error_message': f"Cannot confirm account with {email}. Reason: {str(e.args)}"}), 500

        return jsonify({'message': f"Account {email} has been confirmed."}), 201


@auth.route('/resend_confirmation_code', methods=["POST"])
def resend_confirmation_code():
    data = request.get_json()
    email = data.get('email')
    try:
        secret_hash = cognito.get_secret_hash(email)
        cognito.cognito_client.resend_confirmation_code(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            SecretHash=secret_hash,
            Username=email
        )
    except ClientError as e:
        return jsonify({'error_message': f"Failed resend confirmation code for {email}. Reason: {str(e.args)}"}), 500
    else:
        return jsonify({'message': f"confirmation code has been sent to {email}. "}), 201


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400
    try:
        current_user = user.User.from_email(email)
    except Exception as e:
        return jsonify({'error_message': f'{e}.'}), 400
    else:
        try:
            secret_hash = cognito.get_secret_hash(email)
            auth_result = cognito.cognito_client.admin_initiate_auth(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                AuthFlow="ADMIN_USER_PASSWORD_AUTH",
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password,
                    "SECRET_HASH": secret_hash
                }
            )
        except ClientError as e:
            if e.response['Error']['Code'] == 'UserNotConfirmedException':
                return jsonify({
                    'error_message': 'Account not verified.',
                    'email_verified': current_user.email_verified
                }), 401
            else:
                return jsonify({'error_message': f"Could not verify credentials. {e}"}), 401
        else:
            result = auth_result["AuthenticationResult"]
            return jsonify({
                'access_token': result['AccessToken'],
                'refresh_token': result['RefreshToken'],
                'id_token': result['IdToken'],
                'email_verified': current_user.email_verified,
                'email': current_user.email,
            }), 200


@auth.route("/refresh_token", methods=["POST"])
def refresh_access_token():
    data = request.get_json()
    refresh_token = data.get("refresh_token")
    email = data.get("email")
    refresh_user = user.User.from_email(email)
    secret_hash = cognito.get_secret_hash(refresh_user.cognito_id)

    try:
        response = cognito.cognito_client.admin_initiate_auth(
            UserPoolId=settings.COGNITO_USER_POOL_ID,
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            AuthFlow="REFRESH_TOKEN_AUTH",
            AuthParameters={"REFRESH_TOKEN": refresh_token, "SECRET_HASH": secret_hash},
        )
    except ClientError as e:
        return jsonify({'error_message': f"Cannot refresh access token. Reason: {str(e.args)}"}), 500
    else:
        access_token = response["AuthenticationResult"]["AccessToken"]
        id_token = response["AuthenticationResult"]["IdToken"]
        return jsonify({'access_token': access_token, 'id_token': id_token}), 201


@auth.route("/logout", methods=["GET"])
@multi_auth.login_required
def logout():
    headers = flask.request.headers
    token = headers.get('Authorization').split()[1]
    cognito.cognito_client.global_sign_out(
        AccessToken=token
    )
    return jsonify({"logout_successful": True})


@auth.route("/forgot_password_code", methods=["POST"])
def forgot_password_code():
    data = request.get_json()
    email = data.get('email')
    try:
        secret_hash = cognito.get_secret_hash(email)
        cognito.cognito_client.forgot_password(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            SecretHash=secret_hash,
            Username=email
        )
    except ClientError as e:
        return jsonify({'error_message': f"Cannot create a change password code. Reason: {str(e.args)}"}), 500
    return jsonify({'message': f'Change password code has been sent to {email}'})


@auth.route("/forgot_password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get('email')
    code = data.get('code')
    new_password = data.get('new_password')
    try:
        secret_hash = cognito.get_secret_hash(email)
        cognito.cognito_client.confirm_forgot_password(
            ClientId=settings.COGNITO_APP_CLIENT_ID,
            SecretHash=secret_hash,
            ConfirmationCode=code,
            Password=new_password,
            Username=email
        )
    except ClientError as e:
        response_code = e.response['Error']['Code']
        if response_code == 'ExpiredCodeException' or response_code == 'CodeMismatchException':
            message = f"Cannot change password. Reason: forget password code has expired or is invalid. "
            status_code = 400
        elif response_code == 'LimitExceededException' or response_code == 'TooManyRequestsException':
            message = f"Cannot change password. Reason: too many attempts please wait 15 mins and try again. "
            status_code = 401
        else:
            message = f"Cannot change password. Reason: {str(e.args)}"
            status_code = 500
    else:
        message = f'Password has been changed for {email}'
        status_code = 201
    return jsonify({'error_message': message}), status_code
