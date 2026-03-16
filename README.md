# Uber_Integration_Activation

The aim of this solution is provide a UI interface for interacting with the Uber Marketplace API, specifically the Integration Activation suite to link a merchant store: https://developer.uber.com/docs/eats/references/api/integration_activation_suite

A Flask app is used to provide the interface, interacting with Uber APIs through python code, OAuth 2.0 Authorisation Code flow (for displaying, linking and deleting stores) and Client Credentials (for subsequent requests). 

Pre-requisites: 
- Developer account with Uber - https://developer.uber.com/, which will allow you to link an app, generate Client ID/ Secret and configure a callback URL for Auth Code flow
- Merchant Log in credentials linked to a Store(s)

WIP
