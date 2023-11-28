from typing import TypedDict

class ISTKPush(TypedDict):
    amount: float
    mpesa_number: str

class IB2C(TypedDict):
    amount: float
    mpesa_number: str
    remarks: str
    occassion: str

class IPaymentValidation(TypedDict):
    merchant_id: str
    checkout_id: str

class IMpesaExpressRequest(TypedDict):
    business_short_code: str
    password: str
    timestamp: str
    transaction_type: str
    amount: str
    party_a: str
    party_b: str
    phone_number: str
    callback_url: str
    account_reference: str
    transaction_desc: str

class IRegisterUrlRequest(TypedDict):
    short_code: str
    response_type: str
    confirmation_url: str
    validation_url: str

class IB2CRequest(TypedDict):
    originator_conversation_id: str
    initiator_name: str
    security_credential: str
    command_id: str
    amount: str
    party_a: str
    party_b: str
    remarks: str
    queue_timeout_url: str
    result_url: str
    occasion: str

class ICallbackMetadataItem(TypedDict):
    name: str
    value: str  # Assuming the number can be represented as a string

class IStkCallback(TypedDict):
    merchant_request_id: str
    checkout_request_id: str
    callback_metadata: dict

class IMpesaCallbackData(TypedDict):
    body: dict

class ResultParameter(TypedDict):
    key: str
    value: str  # Assuming the number can be represented as a string

class ReferenceItem(TypedDict):
    key: str
    value: str

class ResultParameters(TypedDict):
    result_parameter: list[ResultParameter]

class ReferenceData(TypedDict):
    reference_item: ReferenceItem

class Result(TypedDict):
    result_type: int
    result_code: int
    result_desc: str
    originator_conversation_id: str
    conversation_id: str
    transaction_id: str
    result_parameters: ResultParameters
    reference_data: ReferenceData

class IB2CResponse(TypedDict):
    result: Result


