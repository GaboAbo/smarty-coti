import environ, logging

from msal import ConfidentialClientApplication

from django.http import HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.views.decorators.cache import never_cache

from .functions import validate_microsoft_token

from App.models import SalesRep

from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)

env = environ.Env()

ENVIRONMENT = env.str("ENV", default="development")

if ENVIRONMENT != 'production':
    environ.Env.read_env()

# Environment Variables
TENANT = env("MICROSOFT_TENANT", default="")
CLIENT_ID = env("MICROSOFT_CLIENT_ID", default="")
CLIENT_SECRET = env("MICROSOFT_CLIENT_SECRET", default="")
REDIRECT_URI = env(
    "MICROSOFT_REDIRECT_URI" if ENVIRONMENT == "production" else "DEVELOPMENT_REDIRECT_URI",
    default=""
)


def set_client():
    return ConfidentialClientApplication(
        CLIENT_ID,
        CLIENT_SECRET,
        authority=f"https://login.microsoftonline.com/{TENANT}",
    )


@never_cache
def microsoft_login(request: HttpRequest) -> HttpResponseRedirect:
    """
    Initiates the Microsoft OAuth2 login flow based on the application type.
    Selects between ConfidentialClientApplication or PublicClientApplication 
    depending on the app_type parameter.

    Args:
        request (HttpRequest): The Django HTTP request object.
        app_type (str): The type of the application. Use 'server' for server-side apps
                        (ConfidentialClientApplication) or 'mobile' for client-side apps
                        (PublicClientApplication). Default is 'server'.

    Returns:
        JsonResponse: A JSON response containing the authorization URL.

    Raises:
        KeyError: If required environment variables are missing.

    Notes:
        - Ensure `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`, and `MICROSOFT_TENANT` are set in the environment.
        - `server` app type requires `ConfidentialClientApplication` (with client secret).
        - `mobile` app type uses `PublicClientApplication` (no client secret).
        - The `auth_flow` stored in the session should not contain sensitive information.
        - Consider storing the redirect URI in an environment variable instead of hardcoding it.
    """   
    _confidential_client = set_client()
    auth_flow = _confidential_client.initiate_auth_code_flow(
        scopes=[f"api://{CLIENT_ID}/User.Read"],
        redirect_uri=REDIRECT_URI,
    )

    auth_url = auth_flow.get("auth_uri")

    request.session["auth_flow"] = auth_flow

    return redirect(auth_url)


@never_cache
def microsoft_callback(request):
    _confidential_client = set_client()
    auth_flow = request.session.pop("auth_flow", None)
    auth_response = request.GET

    if not auth_flow or not auth_response:
        messages.error(request, "Ha ocurrido un error, intente de nuevo.")
        return redirect("/")

    result = _confidential_client.acquire_token_by_auth_code_flow(
        auth_flow, auth_response,
        scopes=[f"api://{CLIENT_ID}/User.Read"]
    )
    
    if not result or "id_token_claims" not in result:
        logger.warning("Microsoft callback failed: Missing id_token_claims or result is empty. Result: %s", result)
        messages.error(request, "Error al autenticar con Microsoft, no posee permisos para utilizar aplicacion.")
        return redirect("/")
    
    access_token = result.get("access_token")
    claims = result.get("id_token_claims")
    
    try:
        validation_result = validate_microsoft_token(access_token)
        if validation_result == "success":
            user_email = claims.get("preferred_username")
            full_name = claims.get("name")
    except AuthenticationFailed as e:
        logger.warning("Microsoft callback failed: Token not valid. Result: %s", result)
        messages.error(request, f"Error al autenticar con Microsoft.")
        return redirect("/")

    user = SalesRep.objects.filter(email=user_email).first()

    if not user:
        messages.error(request, f"Error al autenticar con Microsoft, usuario no enlazado a aplicacion.")
        return redirect("/")
    
    login(request, user)

    request.session["pk"] = user.pk
    request.session["role"] = user.role
    request.session["user_email"] = user_email
    request.session["full_name"] = full_name
    request.session["token"] = result["refresh_token"]
        
    request.session.modified = True

    return redirect("dashboard")


@never_cache
def microsoft_logout(request: HttpRequest, app_type: str = "server"):
    logout(request)
    
    request.session.flush()

    if app_type == "server":
        return redirect("index")
    elif app_type == "mobile":
        return JsonResponse({"status": 200})


def error(request):
    return render(request, "error.html")
