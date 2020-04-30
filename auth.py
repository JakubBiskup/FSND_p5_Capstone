import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'fsndtest.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'BishopGaming'


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_from_cookie():
    authorization = request.cookies.get('token', None)
    if not authorization:
        raise AuthError({'code': 'cookie_missing',
                         'description': 'Cookie expected'}, 401)
    parts = authorization.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({'code': 'invalid_cookie',
                         'description': ("Cookie "
                                         "must start with 'Bearer'")},
                        401)
    elif len(parts) != 2:
        raise AuthError({'code': 'invalid_cookie',
                         'description': ('Cookie'
                                         ' must be bearer token')},
                        401)
    token = parts[1]
    return token


def verify_decode_jwt(token):
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({'code': 'invalid_cookie',
                         'description': 'Authorization malformed'}, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)
        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': ('Incorrect claims. '
                                'Please, check the audience and issuer.')
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_cookie',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({'code': 'invalid_cookie',
                     'description': 'Unable to find the appropriate key.'
                     }, 400)


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({'code': 'permissions_missing',
                         'description': ('"permissions" '
                                         'are expected in token payload')},
                        401)
    if permission not in payload['permissions']:
        raise AuthError({'code': 'not_authorized',
                         'description': ('You do not have permission '
                                         'to perform this action')},
                        403)
    return True


def requires_auth(permission=None):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_from_cookie()
            payload = verify_decode_jwt(token)
            if permission:
                check_permissions(permission, payload)
            return f(*args, **kwargs)

        return wrapper
    return requires_auth_decorator


def get_auth0_user_id_from_cookie_token():
    try:
        token = get_token_from_cookie()
        payload = verify_decode_jwt(token)
        sub = payload['sub']
    except BaseException:
        return None
    return sub


def check_auth(permission):
    token = get_token_from_cookie()
    payload = verify_decode_jwt(token)
    check_permissions(permission, payload)
    return True
