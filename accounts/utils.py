from kavenegar import *
import os

def send_otp_code (phone_number, code):
    print("OTP FUNCTION CALLED", phone_number, code)
    try:
        api = KavenegarAPI(os.getenv("KAVENEGAR_API_KEY"))
        params = {
        'sender': '2000660110',
        'receptor' : phone_number,
        'message' : f'کد تایید شما {code}'
    }   
        response = api.sms_send(params)
        print (response)

    except APIException as e: 
        print(e)
    except HTTPException as e: 
        print(e)

