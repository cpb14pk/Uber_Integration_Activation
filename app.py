from flask import Flask, redirect, request, session, render_template, url_for, flash
import requests
import os
from config import Config
import time
import logging
import json

# Use Logger instead of print for better console output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------- Initialise Flask Server and Config ----------------------

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config["SECRET_KEY"]

# ------------------------ Populate env variables ---------------------------------

CLIENT_ID = os.getenv("UBER_CLIENT_ID")
CLIENT_SECRET = os.getenv("UBER_CLIENT_SECRET")

# ------------------------ Save token for performance/efficiency ---------------
# Ideally, encrypt
token_cache = {
    "token": None,
    "expires_at": 0
}

# ---------------------------- Landing Page -----------------------------------

@app.route("/")
def home():
    return render_template(template_name_or_list="login.html")

# ------------------------------- 1. Login (OAuth)  ---------------------------

# Allow merchants to explicitly authorize app to access stores through OAuth consent
# Use store login and fresh session, nav to create auth url

@app.route("/login")
def login():
    auth_url_full = (
        f"{app.config['AUTH_BASE']}/oauth/v2/authorize"
        f"?client_id={CLIENT_ID}"
        f"&response_type=code"
        f"&redirect_uri={app.config['REDIRECT_URI']}"
        f"&scope=eats.pos_provisioning"
    )

    # redirect to auth url for user login
    return redirect(auth_url_full)

# ------------------------ 2. OAuth Callback ------------------------
#  Use token exchange endpoint to swap the authorization code for a merchant access_token
# -> allow you to make other requests

@app.route("/callback")
def callback():
    error = request.args.get("error")
    if error:
        return f"OAuth failed: {error}", 400
    
    # retrieve code from URL args
    code = request.args.get("code")
    print(code)
    if not code:
        return "No authorization code returned", 400

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        'redirect_uri': app.config['REDIRECT_URI'],
        "code": code,
    }

    response = requests.post(f"{app.config['AUTH_BASE']}/oauth/v2/token",
                             data=data,
                             timeout=30)
    response.raise_for_status()

    # Use this token for store discovery and activation
    token_json = response.json()

    access_token = token_json.get("access_token")
    if not access_token:
        return "Failed to retrieve access token", 400

    session["access_token"] = access_token
    
    # Successful login will show the user dashboard
    return redirect(url_for("dashboard"))


# ------------------------*** Merchant Token Endpoints *** ------------------------

# ------------------------ Dashboard (Get Stores) ------------------------

@app.route("/dashboard")
def dashboard():
    # If the access token has expired, return to landing page
    if "access_token" not in session:
        return redirect(url_for("home"))

    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Accept": "application/json"
    }

    stores_response = requests.get(
        f"{app.config['CORE_API_BASE']}/v1/eats/stores",
        headers=headers,
        timeout=30)

    stores_response.raise_for_status()
    stores = stores_response.json().get("stores", [])
    # logger.info(stores)

    # Render directly instead of redirect
    return render_template("dashboard.html", stores=stores)

# ------------------------ Activate Store (Integration Activation) ------------------------

@app.route("/link_store", methods=["POST"])
def link_store():
    # Make sure the user has an access token
    if "access_token" not in session:
        flash("You need to login first.", "error")
        return redirect(url_for("home"))

    # Get the store_id from the ui table
    store_id = request.form.get("store_id")
    logger.info(f"Linking Store ID {store_id}")

    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {}

    try:
        response = requests.post(
            f"{app.config['CORE_API_BASE']}/v1/eats/stores/{store_id}/pos_data",
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        flash(f"Store {store_id} successfully linked!", "success")
    except requests.exceptions.HTTPError as e:
        logger.error("Store linking failed: %s", response.text)
        error_message = response.json().get("message", "Unknown error")
        flash(f"Store linking failed: {error_message}", "error")
    return redirect(url_for("dashboard"))


# ------------------------ Delete Store (Integration Deletion) ------------------------
@app.route("/delete_store")
def delete_store():
    
    # Make sure the user has an access token
    if "access_token" not in session:
        flash("You need to login first.", "error")
        return redirect(url_for("home"))

    # Get the store_id from the ui table
    store_id = request.args.get("store_id")
    logger.info(f"Linking Store ID {store_id}")

    headers = {
        "Authorization": f"Bearer {session['access_token']}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {}

    try:
        response = requests.delete(
            f"{app.config['CORE_API_BASE']}/v1/eats/stores/{store_id}/pos_data",
            json=payload,
            headers=headers
        )
        response.raise_for_status()

        flash(f"Store {store_id} successfully deleted!", "success")
    except requests.exceptions.HTTPError as e:
        logger.error("Store de-activate failed: %s", response.text)
        error_message = response.json().get("message", "Unknown error")
        flash(f"Store de-activate failed: {error_message}", "error")
    return redirect(url_for("dashboard"))


# ------------------------ Client Credentials Endpoints --------------------
# --------------------------------------------------------------------------


# ------------------------ Get Client Credentials Token --------------------
def get_client_token():
    if token_cache["token"] and time.time() < token_cache["expires_at"]:
        return token_cache["token"]

    response = requests.post(f"{app.config['AUTH_BASE']}/oauth/v2/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "client_credentials",
        "scope": "eats.store eats.order"
    })

    token_json = response.json()

    token_cache["token"] = token_json["access_token"]
    token_cache["expires_at"] = time.time() + token_json["expires_in"] - 60

    return token_cache["token"]

# ------------------------ Menus ------------------------


@app.route("/menus")
def menus():

    store_id = request.args.get("store_id")
    if not store_id:
        return "Missing store_id", 400
    store_name = request.args.get("store_name")

    client_credentials_access_token = get_client_token()

    headers = {
        "Authorization": f"Bearer {client_credentials_access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.get(
        f"{app.config['CORE_API_BASE']}/v2/eats/stores/{store_id}/menus",
        headers=headers,
        timeout=30)

    response.raise_for_status()
    menu_items = response.json()
    display_json = json.dumps(menu_items, indent=2)

    # Illustrating the concept of grabbing menus with client credentials, ideally would display in tabular format 
    return render_template(template_name_or_list="menus.html", store_id=store_id, store_name=store_name, menu_items=display_json)

# ------------------------ Set Store Status ------------------------

@app.route("/storestatus")
def store_status():
    # v1/delivery/store/{store_id}/status
    return


# ------------------------ Logout ------------------------

@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run()
