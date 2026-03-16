# Uber_Integration_Activation

The aim of this solution is provide a friendly user interface for interacting with the Uber Marketplace API, specifically the Integration Activation suite to link a merchant store: https://developer.uber.com/docs/eats/references/api/integration_activation_suite

A Flask app is used to provide the interface, interacting with Uber APIs through python code, OAuth 2.0 Authorisation Code flow (for displaying, linking and deleting stores) and Client Credentials (for subsequent requests). 

Upon login, the merchant is redirected to the Uber auth URL with the scope 'eats.pos_provisioning', where the merchant grants access. The merchant is then redirected to the pre-configured callback url with an authorisation code. This code is then swapped for a merchant access token using client id and secret. This merchant access token can be used for linking a store (integration activation), retrieving store infoprmation and de-activiating the integration. 

Once a store is activated, the user can use client credentials for Store/ Order/ Menu suites. 

Authentication information here: https://developer.uber.com/docs/eats/guides/authentication 

Pre-requisites: 
- Developer account with Uber - https://developer.uber.com/, which will allow you to link an app, generate Client ID/ Secret and configure a callback URL for Auth Code flow
- Merchant Log in credentials linked to a Store(s)

WIP
