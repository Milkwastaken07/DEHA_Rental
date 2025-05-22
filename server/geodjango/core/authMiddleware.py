import jwt
from django.http import JsonResponse
from config import settings
import requests
from jose import jwk, jwt as jose_jwt
from jose.utils import base64url_decode
import logging
from django.utils.deprecation import MiddlewareMixin
from functools import wraps

logger = logging.getLogger(__name__)

class JwtAuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        print("into init")
        self.get_response = get_response
        self.jwks = None
        self.jwks_url = f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}/.well-known/jwks.json"
        self._load_jwks()

    def _load_jwks(self):
        """Fetch JWKS from Cognito"""
        try:
            response = requests.get(self.jwks_url)
            response.raise_for_status()
            self.jwks = response.json()
        except Exception as e:
            logger.error(f"Failed to load JWKS: {e}")
            self.jwks = None

    def _get_public_key(self, kid: str) -> str:
        """Lấy khóa công khai ở định dạng PEM cho kid."""
        for key in self.jwks['keys']:
            if key['kid'] == kid:
                rsa_key = jwk.construct(key)
                pem_key = rsa_key.to_pem().decode('utf-8')
                print(f"Khóa công khai (PEM) cho kid {kid}:\n{str(pem_key)}")
                return pem_key
        raise Exception(f"Không tìm thấy khóa công khai với kid {kid} trong JWKS")

    def __call__(self, request):
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        print("into process view")
        allowed_roles = view_kwargs.get('allowed_roles', [])
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(auth_header)
        if not auth_header or not auth_header.startswith('Bearer '):
            print(f"into: {auth_header}")

            return JsonResponse({'message': 'Unauthorized'}, status=401)

        token = auth_header.split(' ')[1]

        try:
            # Get token headers to find key ID (kid)
            unverified_header = jwt.get_unverified_header(token)
            public_key = self._get_public_key(unverified_header['kid'])
            # print(f"public key: {public_key.to_pem().decode('utf-8')}")
            if not public_key:
                return JsonResponse({'message': 'Invalid token: Public key not found'}, status=400)
            print(f"settings: {settings.COGNITO_APP_CLIENT_ID}, {settings.AWS_REGION}, {settings.COGNITO_USER_POOL_ID}")
            # Verify token with Cognito's public key
            decoded = jose_jwt.decode(
                token,
                public_key,
                algorithms=['RS256'],
                audience=settings.COGNITO_APP_CLIENT_ID,
                issuer=f"https://cognito-idp.{settings.AWS_REGION}.amazonaws.com/{settings.COGNITO_USER_POOL_ID}"
            )
            print(f"decoded: {decoded}")
            user_role = decoded.get('custom:role', '')
            print(f"user role: {user_role}")
            request.custom_user = {
                'id': decoded.get('sub'),
                'role': user_role
            }

            if allowed_roles and user_role.lower() not in [role.lower() for role in allowed_roles]:
                return JsonResponse({'message': 'Access denied'}, status=403)
            print("pass")
            return None
        except jose_jwt.JWTError as e:
            logger.error(f"Failed to decode token: {e}")
            return JsonResponse({'message': 'Invalid token'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return JsonResponse({'message': 'Server error'}, status=500)

        return None

def jwt_auth(allowed_roles=None):
    print(f"into jwt auth: {allowed_roles}")
    if allowed_roles is None:
        allowed_roles = []
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(view_instance, request, *args, **kwargs):
            middleware = JwtAuthMiddleware(lambda req: None)
            result = middleware.process_view(request, view_func, args, {'allowed_roles': allowed_roles})
            if result:
                return result
            return view_func(view_instance, request, *args, **kwargs)
        return wrapped_view
    return decorator