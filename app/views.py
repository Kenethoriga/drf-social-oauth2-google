from django.shortcuts import render
from requests import Response
import requests
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.shortcuts import redirect
from django.views.generic.base import View
from rest_framework.views import APIView
from rest_framework.response import Response            
from rest_framework import status
from .models import *


class GoogleAuthRedirect(View):
    permission_classes = [AllowAny]
    
    def get(self, request):
        redirect_url = f"https://accounts.google.com/o/oauth2/v2/auth?client_id={settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY}&response_type=code&scope=https://www.googleapis.com/auth/userinfo.profile%20https://www.googleapis.com/auth/userinfo.email&access_type=offline&redirect_uri=https://protosapp.pythonanywhere.com/account/google/callback"
        return redirect(redirect_url)
    
class GoogleRedirectURIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Extract the authorization code from the request URL
        code = request.GET.get('code')
        
        if code:
            # Prepare the request parameters to exchange the authorization code for an access token
            token_endpoint = 'https://oauth2.googleapis.com/token'
            token_params = {
                'code': code,
                'client_id': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
                'client_secret': settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
                'redirect_uri': 'Your Redirect URI here',  # Must match the callback URL configured in your Google API credentials
                'grant_type': 'authorization_code',
            }
            
            # Make a POST request to exchange the authorization code for an access token
            response = requests.post(token_endpoint, data=token_params)
            
            if response.status_code == 200:
                access_token = response.json().get('access_token')
                
                if access_token:
                    # Make a request to fetch the user's profile information
                    profile_endpoint = 'https://www.googleapis.com/oauth2/v1/userinfo'
                    headers = {'Authorization': f'Bearer {access_token}'}
                    profile_response = requests.get(profile_endpoint, headers=headers)
                    
                    if profile_response.status_code == 200:
                        data = {}
                        profile_data = profile_response.json()
                        # Proceed with user creation or login
                        user = PersonalAccount.objects.create_user(first_name=profile_data["given_name"], # type: ignore
                                                                    email=profile_data["email"])
                        if "family_name" in profile_data:
                            user.last_name = profile_data["family_name"]
                            user.save
                        refresh = RefreshToken.for_user(user) # type: ignore
                        data['access'] = str(refresh.access_token)
                        data['refresh'] = str(refresh)
                        return Response(data, status.HTTP_201_CREATED)
        
        return Response({}, status.HTTP_400_BAD_REQUEST)