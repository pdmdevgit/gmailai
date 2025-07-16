# OAuth HTTPS Fix for Gmail Authentication

# Add this to the beginning of authenticate_gmail_account function:
import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Replace the redirect URI logic with:
redirect_uri = f"https://{request.host}/api/admin/gmail/callback"
flow.redirect_uri = redirect_uri

# In gmail_oauth_callback function, add:
# Force HTTPS in authorization response URL
auth_response_url = request.url
if auth_response_url.startswith('http://'):
    auth_response_url = auth_response_url.replace('http://', 'https://', 1)

# Use auth_response_url instead of request.url:
flow.fetch_token(authorization_response=auth_response_url)
