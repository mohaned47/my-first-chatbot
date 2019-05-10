from flask import Flask, request

app = Flask(__name__)

FB_API_URL = 'https://graph.facebook.com/v2.6/me/messages'
VERIFY_TOKEN = '9ahwtii'
PAGE_ACCESS_TOKEN = 'EAAEIvbYvr2kBANpDsc2Dh7G9PeiRaq55RRTZCacvFXZCuzAYPTgQ8ufqSpYaZCdZBlPj2GIzIjlvsUdUTnuNGgbllPY3mOfutPw2wCe8Tzc824rd8muL6G8RsNYLNdXycp3xVj9fgeZBlCn9kSdjMxnJofHYUI7lSEROZBCDzsSgN4XlK2Ww2h'

def replace_pronouns(message):
    message = message.lower()
    if 'me' in message:
        return re.sub('me','you',message)
    if 'my' in message:
        return re.sub('my','your',message)
    if 'your' in message:
        return re.sub('your','my',message)
    if 'you' in message:
        return re.sub('you','me',message)
    return message

def match_rule(rules, message):
    response, phrase = "default", None
    for pattern, responses in rules.items():
        match = re.search(pattern,message)
        if match is not None:
            response = random.choice(responses)
            if '{0}' in response:
                phrase = match.group(1)
    return response.format(phrase)
def chitchat_response(message):
    response, phrase = match_rule(eliza_rules,message)
    if response == "default":
        return None
    if '{0}' in response:
        phrase = replace_pronouns(phrase)
        response = response.format(phrase)
    return response
def send_message(state,pending,message):
    print("USER : {}".format(message))
    response = chitchat_response(message)
    if response is not None:
        print("BOT : {}".format(response))
        return state, None
    new_state, response, pending_state = policy_rules[(state, interpret(message))]
    print("BOT : {}".format(response))
    if pending is not None:
        new_state, response, pending_state = policy_rules[pending]
        print("BOT : {}".format(response))        
    if pending_state is not None:
        pending = (pending_state, interpret(message))
    return new_state, pending
def send_messages(messages):
    state = INIT
    pending = None
    for msg in messages:
        state, pending = send_message(state, pending, msg)

send_messages([
    "I'd like to order some coffee",
    "555-12345",
    "do you remember when I ordered 1000 kilos by accident?",
    "kenyan"
])  

def get_bot_response(message):
    return send_messages(message)


def verify_webhook(req):
    if req.args.get("hub.verify_token") == VERIFY_TOKEN:
        return req.args.get("hub.challenge")
    else:
        return "incorrect"

def respond(sender, message):
    response = get_bot_response(message)
    send_message(sender, response)


def is_user_message(message):
    return (message.get('message') and
            message['message'].get('text') and
            not message['message'].get("is_echo"))


@app.route("/webhook")
def listen():
    if request.method == 'GET':
        return verify_webhook(request)

    if request.method == 'POST':
        payload = request.json
        event = payload['entry'][0]['messaging']
        for x in event:
            if is_user_message(x):
                text = x['message']['text']
                sender_id = x['sender']['id']
                respond(sender_id, text)

        return "ok"
