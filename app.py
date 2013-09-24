import os

from flask import Flask
from flask import Response
from flask import request
from flask import render_template
from twilio import twiml
from twilio.rest import TwilioRestClient
import twilio
from twilio.rest import TwilioRestClient


# Pull in configuration from system environment variables
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_NUMBER = os.environ.get('TWILIO_NUMBER')

# create an authenticated client that can make requests to Twilio for your
# account.
client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Create a Flask web app
app = Flask(__name__)

recording_url_dict = {}

# Render the home page
@app.route('/')
def index():
    return render_template('index.html')

# Handle a POST request to send a text message. This is called via ajax
# on our web page
@app.route('/message', methods=['POST'])
def message():
    # Send a text message to the number provided
    message = client.sms.messages.create(to=request.form['to'],
                                         from_=TWILIO_NUMBER,
                                         body='Good luck on your Twilio quest!')

    # Return a message indicating the text message is enroute
    return 'Message on the way!'

# Handle a POST request to make an outbound call. This is called via ajax
# on our web page
@app.route('/call', methods=['POST'])
def call():
    # Make an outbound call to the provided number from your Twilio number
    call = client.calls.create(to=request.form['to'], from_=TWILIO_NUMBER, 
                               url='http://twimlets.com/message?Message%5B0%5D=http://demo.kevinwhinnery.com/audio/zelda.mp3')

    # Return a message indicating the call is coming
    return 'Call inbound!'

# Generate TwiML instructions for an outbound call
@app.route('/hello')
def hello():
    response = twiml.Response()
    response.say('Hello there! You have successfully configured a web hook.')
    response.say('Good luck on your Twilio quest!', voice='woman')
    return Response(str(response), mimetype='text/xml')

@app.route('/incoming/sms', methods=['GET'])
def incomingSMS():
    response = """
<Response>
    <Sms>I just responded to a text message. Huzzah!</Sms>
    </Response>
    """

    # Return a message indicating the text message is enroute
    return response

@app.route('/incoming/call', methods=['POST'])
def incomingCall():
#with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
#is the same as <Gather numDigits=1 action="/handle-key"></Gather>
    response = """
<Response>
    <Gather numDigits="1" action="/handle-key" method="POST" timeout="10" finishOnKey="*">
        <Say> Press 1 to record a message or press 2 to play back the last recorded message..</Say>
    </Gather>
</Response>
    """
    # Return a message indicating the text message is enroute
    return response

@app.route('/handle-key', methods=['GET', 'POST'])
def handle_key():
 
    # Get the digit pressed by the user
    digit_pressed = request.values.get('Digits', None)
    resp = twilio.twiml.Response()
    if digit_pressed == "1":
        resp.say("Record your message at the tone. Press the star key when finished.")
        resp.record(numDigits=1, action="/handle-recording", playBeep=True, maxLength="20", finishOnKey="*", method="GET")
        #if no messege was recorded
        resp.say("No message was recorded.")
    elif digit_pressed == "2":
        resp.say("Playing back the last recorded message.")     
        resp.play(recording_url_dict["recording_url"])
    #Sidequest: When the user presses zero, skip right to talking to a human! Forward the call to your own mobile phone. Rewards: 50 XP
    elif digit_pressed == "0":
        # Dial phone - connect that number to the incoming caller.
        resp.dial("+16503958420")
        # If the dial fails:
        resp.say("The call failed, or the remote party hung up. Goodbye.")
 
     # If the caller pressed anything but 1 or 0, redirect them to the homepage.
    else:
        resp.say("You didn't press 1, so you must not like surprises. Goodbye.")
    
    return str(resp)

@app.route('/handle-recording', methods=['GET', 'POST'])
def handle_recording():
    recording_url = request.values.get('RecordingUrl', None)
    #print recording_url
    recording_url_dict["recording_url"] = recording_url

    return """<Response><Say>Callback to listen to the last recording!</Say></Response>"""

#Sidequest: Use the REST API to pull down the last three recordings for your account, and play all three instead of just one
account_sid = "AC992eb1da594c3c5f691825a2e51b5b37"
auth_token  = "{{ 052d8906b957d9d49fa004a87436ca46 }}"
client = TwilioRestClient(account_sid, auth_token)
 #client.recordings.delete("RE557ce644e5ab84fa21cc21112e22c485")


if __name__ == '__main__':
    # Note that in production, you would want to disable debugging
    app.run(debug=True)


