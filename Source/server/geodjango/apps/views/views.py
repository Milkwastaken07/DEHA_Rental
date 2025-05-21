from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from core.authMiddleware import jwt_auth
# Create your views here.
class HelloWorld(APIView):
    # @jwt_auth(allowed_roles=['manager'])
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({"message": "Hello-world"})

