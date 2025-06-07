from flask import Flask, request, Response
from twilio.rest import Client
import os

app = Flask(__name__)

# שמירת תשובות לפי תנור
oven_responses = {}

@app.route('/request_permission', methods=['GET'])
def request_permission():
    oven_id = request.args.get('oven_id', 'default')
    oven_responses[oven_id] = 'pending'

    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')
    to_number = os.environ.get('TARGET_PHONE_NUMBER')

    if not all([account_sid, auth_token, from_number, to_number]):
        return 'Missing environment variables', 500

    client = Client(account_sid, auth_token)

    call = client.calls.create(
        url=f"https://bar-mitzva-oven-server.onrender.com/twiml?oven_id={oven_id}",
        to=to_number,
        from_=from_number
    )

    return f"Call initiated to {to_number} with SID {call.sid}", 200


@app.route('/twiml', methods=['GET', 'POST'])
def twiml():
    oven_id = request.args.get('oven_id', 'default')

    audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"

    xml = f'''
    <Response>
        <Play>{audio_url}</Play>
        <Gather numDigits="1" action="/handle_response?oven_id={oven_id}" method="POST" timeout="10" finishOnKey="">
            <Say>Press 1 to allow. Press 2 to deny.</Say>
        </Gather>
    </Response>
    '''
    return Response(xml, mimetype='text/xml')


@app.route('/handle_response', methods=['POST'])
def handle_response():
    digit = request.form.get('Digits')
    oven_id = request.args.get('oven_id', 'default')

    if digit == '1':
        oven_responses[oven_id] = 'granted'
    elif digit == '2':
        oven_responses[oven_id] = 'denied'
    else:
        oven_responses[oven_id] = 'invalid'

    print(f"📞 Oven {oven_id} response: {oven_responses[oven_id]}")

    return '<Response><Say>Thank you. Your response was received.</Say></Response>', 200
