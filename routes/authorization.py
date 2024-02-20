from flask import Blueprint, request, jsonify
import requests
import base64

auth_bp = Blueprint('auth', __name__)

def validate_authorization(func):
    def wrapper(*args, **kwargs):
        # Get the Authorization header from the request
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            print('Authorization header is missing')
            return jsonify({'error': 'Authorization header is missing'}), 401

        # Get the Token part
        token = auth_header.split(' ')[1]

        # Check if the token is present
        if not token:
            print('Token is missing')
            return jsonify({'error': 'token is missing'}), 401

        # Validate the Authorization token (You can implement your specific logic here)
        # For example, you might check if the token is valid or if the user has the right permissions
        if not is_valid_token(token):
            print('Invalid authorization token')
            return jsonify({'error': 'Invalid authorization token'}), 401

        # If the token is valid, proceed to the original route function
        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper

def is_valid_token(token):
    # Send a request to Google API tokeninfo endpoint
    response = requests.get("https://www.googleapis.com/oauth2/v1/tokeninfo", params={'id_token': token})

    # Check if the response is successful and the token is valid
    if response.status_code == 200:
        return True 
    else:
        return False
    
@auth_bp.route('/token', methods=['POST'])
def token():
    code = request.form.get('code')
    redirect_uri = request.form.get('redirect_uri')
    grant_type = request.form.get('grant_type')

    authorization = request.headers.get('Authorization')
    client_id = None
    client_secret = None
    if authorization:
        auth_string = authorization.split(' ')[1]
        decoded_auth_string = base64.b64decode(auth_string).decode('utf-8')
        client_id, client_secret = decoded_auth_string.split(':')
    else:
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        
    

    # Make a request to Google's token endpoint
    google_token_url = 'https://oauth2.googleapis.com/token'

    google_data = {
        'code': code,
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri,
        'grant_type': grant_type
    }



    response = requests.post(google_token_url, data=google_data)

    # Process the Google response and return the id_token as access_token
    google_response = response.json()
    id_token = google_response.get('id_token')
    token_type = google_response.get('token_type')
    scope = google_response.get('scope')
    result_refresh_token = google_response.get('refresh_token')
    expires_in = google_response.get('expires_in')

    if result_refresh_token:
        return jsonify({'access_token': id_token,
                    'token_type': token_type,
                    'scope': scope,
                    'refresh_token': result_refresh_token,
                    'expires_in': expires_in})
    else:
        return jsonify({'access_token': id_token,
                    'token_type': token_type,
                    'scope': scope,
                    'expires_in': expires_in})
    
@auth_bp.route('/refresh', methods=['POST'])
def refresh():
    # Get the refresh token and grant type from the request
    refresh_token = request.form.get('refresh_token')
    grant_type = request.form.get('grant_type')
   
    authorization = request.headers.get('Authorization')
    client_id = None
    client_secret = None
    if authorization:
        auth_string = authorization.split(' ')[1]
        decoded_auth_string = base64.b64decode(auth_string).decode('utf-8')
        client_id, client_secret = decoded_auth_string.split(':')
    else:
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')

    # Define the Google token URL
    google_token_url = "https://oauth2.googleapis.com/token"

    # Define the data to send in the request
    google_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": grant_type,
    }

    # Make the request to Google's token endpoint
    response = requests.post(google_token_url, data=google_data)
    google_response = response.json()

    # If the request was successful, the refresh token is valid
    if response.status_code == 200:
        id_token = google_response.get('id_token')
        token_type = google_response.get('token_type')
        scope = google_response.get('scope')
        expires_in = google_response.get('expires_in')

        return jsonify({'access_token': id_token,
            'token_type': token_type,
            'scope': scope,
            'expires_in': expires_in}
        )
    else:
        # If the request was not successful, the refresh token is valid
        return jsonify({'error': 'Invalid refresh token'}), 400
