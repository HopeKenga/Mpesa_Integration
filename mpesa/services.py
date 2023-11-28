import base64
from datetime import datetime
import requests
from django.conf import settings
from .models import MpesaTransaction, B2CTransaction
from .mpesa_types import ISTKPush, IB2C, IB2CRequest, IMpesaCallbackData, IMpesaExpressRequest, IRegisterUrlRequest, \
    IB2CResponse

# Utility Functions
def get_timestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")

def lipa_na_mpesa_password():
    short_code = settings.MPESA_SHORTCODE
    pass_key = settings.MPESA_PASSKEY
    timestamp = get_timestamp()
    return base64.b64encode(f"{short_code}{pass_key}{timestamp}".encode()).decode('utf-8')

# Service Functions
def get_oauth_token():
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET
    auth_string = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode('utf-8')
    headers = {'Authorization': f'Basic {auth_string}'}
    try:
        response = requests.get(f"{settings.SAFARICOM_URL}oauth/v1/generate?grant_type=client_credentials", headers=headers)
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.RequestException as e:
        print(f"Error obtaining access token: {e}")
        return None

def stk_push(data: ISTKPush):
    payload = build_stk_push_payload(data['amount'], data['mpesa_number'])
    headers = {'Authorization': f'Bearer {get_oauth_token()}'}
    try:
        response = requests.post(f"{settings.SAFARICOM_URL}mpesa/stkpush/v1/processrequest", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error in stk_push: {e}")
        return str(e)

def register_url():
    payload = build_register_url_payload()
    headers = {'Authorization': f'Bearer {get_oauth_token()}'}
    try:
        response = requests.post(f"{settings.SAFARICOM_URL}mpesa/c2b/v2/registerurl", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error in register_url: {e}")
        return None
def b2c(data: IB2C):
    payload = build_b2c_payload(data['amount'], data['mpesa_number'], data['remarks'], data['occassion'])
    headers = {'Authorization': f'Bearer {get_oauth_token()}'}
    try:
        response = requests.post(f"{settings.SAFARICOM_URL}mpesa/b2c/v3/paymentrequest", json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error in b2c: {e}")
        return None

def express_callback(data: IMpesaCallbackData):
    callback_data = data['body']['stkCallback']
    merchant_request_id = callback_data['MerchantRequestID']
    checkout_request_id = callback_data['CheckoutRequestID']
    result_code = callback_data.get('ResultCode', None)
    result_desc = callback_data.get('ResultDesc', None)
    callback_metadata = callback_data.get('CallbackMetadata', {})

    transaction_id = None
    transaction_time = None
    phone_number = None
    transaction_amount = None

    if 'Item' in callback_metadata:
        for item in callback_metadata['Item']:
            if item['Name'] == 'MpesaReceiptNumber':
                transaction_id = item['Value']
            elif item['Name'] == 'TransactionDate':
                transaction_time = item['Value']
            elif item['Name'] == 'PhoneNumber':
                phone_number = item['Value']
            elif item['Name'] == 'Amount':
                transaction_amount = float(item['Value'])

    mpesa_transaction = MpesaTransaction.objects.create(
        merchant_request_id=merchant_request_id,
        checkout_request_id=checkout_request_id,
        transaction_id=transaction_id,
        transaction_time=transaction_time,
        phone_number=phone_number,
        transaction_amount=transaction_amount,
        result_code=result_code,
        result_desc=result_desc
    )

    return mpesa_transaction.id

def b2c_callback(data: IB2CResponse):
    result_parameters = data['result']['result_parameters']['result_parameter']
    result_values = {param['key']: param['value'] for param in result_parameters}

    transaction_amount = float(result_values.get('TransactionAmount', 0))
    transaction_receipt = result_values.get('TransactionReceipt', '')
    receiver_party_public_name = result_values.get('ReceiverPartyPublicName', '')
    transaction_completed_datetime = result_values.get('TransactionCompletedDateTime', '')
    b2c_recipient_is_registered_customer = result_values.get('B2CRecipientIsRegisteredCustomer', '')
    b2c_utility_account_available_funds = float(result_values.get('B2CUtilityAccountAvailableFunds', 0))
    b2c_working_account_available_funds = float(result_values.get('B2CWorkingAccountAvailableFunds', 0))

    b2c_transaction = B2CTransaction.objects.create(
        transaction_amount=transaction_amount,
        transaction_receipt=transaction_receipt,
        receiver_party_public_name=receiver_party_public_name,
        transaction_completed_datetime=transaction_completed_datetime,
        b2c_recipient_is_registered_customer=b2c_recipient_is_registered_customer,
        b2c_utility_account_available_funds=b2c_utility_account_available_funds,
        b2c_working_account_available_funds=b2c_working_account_available_funds
    )

    return b2c_transaction.id

# Database Interaction Functions
def create_mpesa_transaction(data):
    return MpesaTransaction.objects.create(
        merchant_request_id=data['merchantRequestID'],
        checkout_request_id=data['checkoutRequestID'],
        transaction_id=data['transactionID'],
        transaction_time=data['transactionTime'],
        phone_number=data['phoneNumber'],
        transaction_amount=data['transactionAmount']
    )

# Helper Functions for Building Payloads
def build_stk_push_payload(amount, mpesa_number):
    timestamp = get_timestamp()
    return {
        'BusinessShortCode': settings.MPESA_SHORTCODE,
        'Password': lipa_na_mpesa_password(),
        'Timestamp': timestamp,
        'TransactionType': "CustomerPayBillOnline",
        'Amount': str(amount),
        'PartyA': mpesa_number,
        'PartyB': settings.MPESA_SHORTCODE,
        'PhoneNumber': mpesa_number,
        'CallBackURL': f"{settings.MPESA_CALLBACK_URL}express/callback/url",
        'AccountReference': "AccountRef",
        'TransactionDesc': "Payment"
    }

def build_register_url_payload():
    return {
        'ShortCode': settings.MPESA_SHORT_CODE,
        'ResponseType': "Completed",
        'ConfirmationURL': f"{settings.MPESA_CALLBACK}payment/confirmation",
        'ValidationURL': f"{settings.MPESA_CALLBACK}validation",
    }

def build_b2c_payload(amount, mpesa_number, remarks, occassion):
    return {
        'OriginatorConversationID': "jkdsjbdcsjk",  # Generate or use a relevant ID
        'InitiatorName': settings.INITIATOR_NAME,
        'SecurityCredential': "",  # Use actual security credential
        'CommandID': "BusinessPayment",
        'Amount': str(amount),
        'PartyA': settings.MPESA_SHORT_CODE,
        'PartyB': mpesa_number,
        'Remarks': remarks,
        'QueueTimeOutURL': f"{settings.MPESA_CALLBACKURL}b2c/queue",
        'ResultURL': f"{settings.MPESA_CALLBACKURL}b2c/result",
        'Occassion': occassion,
    }

