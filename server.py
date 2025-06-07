from flask import Flask, request
from twilio.rest import Client
import os

app = Flask(__name__)

@app.route('/request_permission', methods=['GET'])
def request_permission():
    # מזהה התנור (למשל "2")
    oven_id = request.args.get('oven_id', 'default')

    # פרטי Twilio מתוך משתני סביבה
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')
    to_number = os.environ.get('TARGET_PHONE_NUMBER')

    if not all([account_sid, auth_token, from_number, to_number]):
        return 'Missing environment variables', 500

    client = Client(account_sid, auth_token)

    # שליחת שיחה עם הודעה קולית בלבד – בלי Gather
    call = client.calls.create(
        twiml=f'''
        <Response>
            <Say language="he-IL" voice="Polly.Carmit">
                הופעלה בקשה להפעלת תנור מספר {oven_id}.
                אם לא אתם ביקשתם זאת, אנא פנו לאחראי.
            </Say>
        </Response>
        ''',
        to=to_number,
        from_=from_number
    )

    return f"Call initiated to {to_number} with SID {call.sid}", 200


if __name__ == '__main__':
    app.run(debug=True)
