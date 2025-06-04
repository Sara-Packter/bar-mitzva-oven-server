from flask import Flask, request, jsonify
from twilio.rest import Client
import os

app = Flask(__name__)

# זיכרון זמני לשמירת תשובות לפי תנור
oven_responses = {}

# קריאה להתחלת שיחה
@app.route('/request_permission', methods=['GET'])
def request_permission():
    # מזהה התנור (למשל "2")
    oven_id = request.args.get('oven_id', 'default')

    # שמור תשובה זמנית
    oven_responses[oven_id] = 'pending'

    # פרטי Twilio
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')
    to_number = os.environ.get('TARGET_PHONE_NUMBER')

    if not all([account_sid, auth_token, from_number, to_number]):
        return 'Missing environment variables', 500

    client = Client(account_sid, auth_token)

    # יצירת שיחה עם הודעה קולית
    call = client.calls.create(
        twiml=f'''
        <Response>
            <Say language="he-IL" voice="Polly.Carmit">
                האם לאשר הפעלת תנור? לחץ 1 לאישור, או 2 לדחייה.
            </Say>
            <Gather numDigits="1" action="/handle_response?oven_id={oven_id}" method="POST" timeout="10"/>
        </Response>
        ''',
        to=to_number,
        from_=from_number
    )

    return f"Call initiated to {to_number} with SID {call.sid}", 200


# קבלת תגובת המשתמש (לחיצה)
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

    return '<Response><Say>תודה. התקבלה תשובתך.</Say></Response>', 200


# שאילתת תשובה מהצד של ה-ESP32
@app.route('/get_response', methods=['GET'])
def get_response():
    oven_id = request.args.get('oven_id', 'default')
    status = oven_responses.get(oven_id, 'pending')

    if status == 'granted':
        return jsonify({"status": "yes"})
    elif status == 'denied':
        return jsonify({"status": "no"})
    else:
        return jsonify({"status": "pending"})

if __name__ == '__main__':
    app.run(debug=True)
