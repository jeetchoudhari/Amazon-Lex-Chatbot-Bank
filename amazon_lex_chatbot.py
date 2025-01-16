"""
How does AWS Lambda cheer up Amazon Lex? By saying, "Don't worry, I've got your back(end)!"

- NextWork :) 
"""
import json
import random
import decimal

# Account balances for Savings and Checking
account_balances = {
    "savings": decimal.Decimal("1000.00"),
    "checking": decimal.Decimal("500.00"),
    "credit": {
        "visa": decimal.Decimal("2000.00"),
        "mastercard": decimal.Decimal("1500.00"),
        "amex": decimal.Decimal("3000.00"),
        "american express": decimal.Decimal("3000.00")  # Alias for Amex
    }
}

# Generate a random number (used for demo purposes)
def random_num():
    return decimal.Decimal(random.randrange(1000, 50000)) / 100

# Retrieve all slots from the user's request
def get_slots(intent_request):
    return intent_request['sessionState']['intent']['slots']

# Retrieve a specific slot value
def get_slot(intent_request, slotName):
    slots = get_slots(intent_request)
    if slots is not None and slotName in slots and slots[slotName] is not None:
        return slots[slotName]['value']['interpretedValue']
    else:
        return None

# Retrieve session attributes
def get_session_attributes(intent_request):
    sessionState = intent_request['sessionState']
    if 'sessionAttributes' in sessionState:
        return sessionState['sessionAttributes']
    return {}

# Generate a response to elicit a new intent
def elicit_intent(intent_request, session_attributes, message):
    return {
        'sessionState': {
            'dialogAction': {
                'type': 'ElicitIntent'
            },
            'sessionAttributes': session_attributes
        },
        'messages': [message] if message != None else None,
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }

# Close the conversation and return a response
def close(intent_request, session_attributes, fulfillment_state, message):
    intent_request['sessionState']['intent']['state'] = fulfillment_state
    return {
        'sessionState': {
            'sessionAttributes': session_attributes,
            'dialogAction': {
                'type': 'Close'
            },
            'intent': intent_request['sessionState']['intent']
        },
        'messages': [message],
        'sessionId': intent_request['sessionId'],
        'requestAttributes': intent_request['requestAttributes'] if 'requestAttributes' in intent_request else None
    }

# Check Balance intent handler
def CheckBalance(intent_request):
    session_attributes = get_session_attributes(intent_request)
    account = get_slot(intent_request, 'accountType').lower()
    balance = account_balances.get(account, "0.00")
    text = f"Thank you. The balance on your {account} account is ${balance} dollars."
    message = {
        'contentType': 'PlainText',
        'content': text
    }
    fulfillment_state = "Fulfilled"
    return close(intent_request, session_attributes, fulfillment_state, message)

# Transfer Funds intent handler
def TransferFunds(intent_request):
    session_attributes = get_session_attributes(intent_request)
    from_account = get_slot(intent_request, 'sourceAccountType').lower()
    to_account = get_slot(intent_request, 'targetAccountType').lower()
    amount = decimal.Decimal(get_slot(intent_request, 'amount'))

    if from_account in account_balances and to_account in account_balances:
        if account_balances[from_account] >= amount:
            account_balances[from_account] -= amount
            account_balances[to_account] += amount
            text = f"Transferred ${amount} from your {sourceAccountType} account to your {targetAccountType} account."
        else:
            text = f"Insufficient funds in your {sourceAccountType} account to transfer ${amount}."
    else:
        text = f"Invalid account type. Please specify 'savings' or 'checking' or 'Credit'."
    
    message = {
        'contentType': 'PlainText',
        'content': text
    }
    fulfillment_state = "Fulfilled"
    return close(intent_request, session_attributes, fulfillment_state, message)

# Dispatch the user's intent to the appropriate handler
def dispatch(intent_request):
    intent_name = intent_request['sessionState']['intent']['name']

    if intent_name == 'CheckBalance':
        return CheckBalance(intent_request)
    elif intent_name == 'TransferFunds':
        return TransferFunds(intent_request)

    raise Exception(f"Intent with name {intent_name} not supported")

# Lambda entry point
def lambda_handler(event, context):
    response = dispatch(event)
    return response
