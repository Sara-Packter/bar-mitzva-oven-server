from flask import Flask, request, Response
from twilio.rest import Client
import os

app = Flask(__name__)

@app.route('/request_permission', methods=['GET'])
def request_permission():
    oven_id = request.args.get('oven_id', 'default')

    # פרטי Twilio מהסביבה
    account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    from_number = os.environ.get('TWILIO_PHONE_NUMBER')
    to_number = os.environ.get('TARGET_PHONE_NUMBER')

    if not all([account_sid, auth_token, from_number, to_number]):
        return 'Missing environment variables', 500

    client = Client(account_sid, auth_token)

    # שליחת שיחה שמריצה TwiML חיצוני עם הקלטה
    call = client.calls.create(
        url=f"https://bar-mitzva-oven-server.onrender.com/twiml?oven_id={oven_id}",
        to=to_number,
        from_=from_number
    )

    return f"Call initiated to {to_number} with SID {call.sid}", 200


@app.route('/twiml', methods=['GET', 'POST'])
def twiml():
    # כתובת של קובץ MP3 (למשל הקלטה ששלחת לשרת קבצים או אפילו קישור זמני ל-Google Drive/Dropbox/S3)
    audio_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3"  # לדוגמה

    xml = f'''
    <Response>
        <Play>{audio_url}</Play>
    </Response>
    '''
    return Response(xml, mimetype='text/xml')


if __name__ == '__main__':
    app.run(debug=True)
