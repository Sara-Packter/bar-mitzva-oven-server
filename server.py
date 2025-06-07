from flask import Flask, request, jsonify, Response
from twilio.rest import Client
import os

app = Flask(__name__)

# זיכרון זמני לשמירת תשובות לפי תנור
oven_responses = {}

# קריאה להתחלת שיחה
@app.route('/request_permission', methods=['GET'])
def request_permission():
    oven_id = request.args.get('oven_id', 'default')

    # איפוס תשובה קודמת
    oven_responses[oven_id] = 'pending'

    # פרטי טוויליו מהסביבה
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')
    to_number = os.environ.get('TARGET_PHONE_NUMBER')

    if not all([account_sid, auth_token, from_number, to_number]):
        return 'Missing environment variables', 500

    client = Client(account_sid, auth_token)

    # יוצרים שיחה ומפנים את טוויליו ל-URL שלנו
    call = client.calls.create(
        url=f"https://bar-mitzva-oven-server.onrender.com/twiml?oven_id={oven_id}",
        to=to_number,
        from_=from_number
    )

    return f"Call initiated to {to_number} with SID {call.sid}", 200


# TwiML Response שמוקרא בשיחה
@app.route('/twiml', methods=['GET', 'POST'])
def twiml():
    oven_id = request.args.get('oven_id', 'default')

    xml = f'''
    <Response>
        <Say language="he-IL" voice="Polly.Carmit">
            האם לאשר הפעלת תנור מספר {oven_id}? לחץ 1 לאישור, או 2 לדחייה.
        </Say>
        <Gather numDigits="1" action="/handle_response?oven_id={oven_id}" method="POST" timeout="10"/>
    </Response>
    '''

    return Response(xml, mimetype='application/xml')


# קבלת התגובה מהמשתמש (1/2)
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


# שליפת סטטוס ל-ESP
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
