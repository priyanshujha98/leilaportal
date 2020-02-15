#! /usr/bin/env python3.6

"""
server.py
Stripe Sample.
Python 3.6 or newer required.
"""

import stripe
import json
import os
import requests

#flask

from flask import Flask, render_template, jsonify, request, send_from_directory, session, Session
# from flask_session import Session
from dotenv import load_dotenv, find_dotenv

# Sendgrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Setup Stripe python client library
load_dotenv(find_dotenv())
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
stripe.api_version = os.getenv('STRIPE_API_VERSION')

static_dir = str(os.path.abspath(os.path.join(
    __file__, "..", os.getenv("STATIC_DIR"))))
app = Flask(__name__, static_folder=static_dir,
            static_url_path="", template_folder=static_dir)

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
app.secret_key = "ilnzdfsdf"
# app.config['SERVER_NAME'] = 'https://leila-267909.appspot.com'
# app.config['SECRET_KEY'] = 'ilnzdfsdf'
# Session(app)


@app.route('/', methods=['GET'])
def get_example():
    return render_template('index.html')


@app.route('/config', methods=['GET'])
def get_publishable_key():
    return jsonify({
      'publicKey': os.getenv('STRIPE_PUBLISHABLE_KEY'),
      'basePrice': os.getenv('BASE_PRICE'),
      'currency': os.getenv('CURRENCY')
    })

# Fetch the Checkout Session to display the JSON result on the success page
@app.route('/checkout-session', methods=['GET'])
def get_checkout_session():

    #TODO: if session[patient] != 0
    id = request.args.get('sessionId')
    checkout_session = stripe.checkout.Session.retrieve(id)

    print('check:, ' + session['patient'])

    message = Mail(
        from_email='manummasson8@gmail.com',
        to_emails='manummasson8@gmail.com',
        subject='New request for ' + session.get('medication', 'NULL/notset') + ' by ' + session.get('patient', 'NULL/notset'),
        html_content='<li><h2>From: </h2>' + session.get('patient', 'NULL/notset') + "at " + session.get('email', 'NULL/notset') + ', ' + session.get('phone', 'NULL/notset') +'</li>'
                     + '<li><h2>Medication: </h2><h3>' + session.get('medication', 'NULL/notset') + '</h3></li>'
                     + '<li><h2>Pharmacy: </h2><h3>' + session.get('pharmacy', 'NULL/notset') + '</h3></li>'
                     + '<li><h2>Notes: </h2> <h3>' + session.get('notes', 'NULL/notset') + '</h3></li>'
    )
    try:
        sg = SendGridAPIClient('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')
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
    # session['patient'] = 0
    print("Test?")
    return jsonify(checkout_session)



@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    data = json.loads(request.data)
    domain_url = os.getenv('DOMAIN')
    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - lets capture the payment later
        # [customer_email] - lets you prefill the email input in the form
        # For full details see https:#stripe.com/docs/api/checkout/sessions/create
        
        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        print(data)
        session['patient'] = data['patient']
        session['email'] = data['email']
        session['phone'] = data['phone']
        session['medication'] = data['medication']
        session['pharmacy'] = data['pharmacy']
        session['notes'] = data['notes']
        print("no get: ", session['patient'])
        print("with get: ", session.get('patient', 'NULL/notset'))
        session.modified = True

        checkout_session = stripe.checkout.Session.create(
            success_url=domain_url +
            "/success.html?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "/canceled.html",
            payment_method_types=["card"],
            line_items=[
                {
                    "name": "Script",
                    "quantity": data['quantity'],
                    "currency": os.getenv('CURRENCY'),
                    "amount": os.getenv('BASE_PRICE')
                }
            ]
        )
        return jsonify({'sessionId': checkout_session['id']})
    except Exception as e:
        return jsonify(e), 40


@app.route('/webhook', methods=['POST'])
def webhook_received():
    # You can use webhooks to receive information about asynchronous payment events.
    # For more about our webhook events check out https://stripe.com/docs/webhooks.
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('Payment succeeded!')


    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(port=4242)
