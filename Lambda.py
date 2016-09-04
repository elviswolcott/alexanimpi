import smtplib
import email.mime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#equivalent of main()
def lambda_handler(event, context):
    if (event['session']['application']['applicationId'] != "amzn1.ask.skill.8aa5defe-18b9-4d76-822c-f6b24c2c8287"):
        raise ValueError("Invalid Application ID") #weed out requests from other skills

    if event['session']['new']:
        event['session']['attributes'] = build_attributes(None, None, None, None, 3, 5, 6, None, None, None)
    if event['request']['type'] == "LaunchRequest":
        return simple_response(build_attributes(None, None, None, None, 3, 5, 6, None, None, None), "Start", "This is the game of nim, tell me to start a game or ask for instructions", "Try saying tell me how to play nim", False)
    elif event['request']['type'] == "IntentRequest":
        return intent_dispatcher(event['request']['intent'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return None
#returns the appropriate response with session data etc. correct
def intent_dispatcher(intent, session):
    name = intent['name']
    if name == "SelectIntent":
        a = int(session['attributes']['state'][0])
        b = int(session['attributes']['state'][1])
        c = int(session['attributes']['state'][2])
        if amount_present(session):
            if int(intent['slots']['Selection']['value']) < 1 or int(intent['slots']['Selection']['value']) > 3:
                return error_response(session, "That group doesn't exist. Please choose a different one.", "You choose a group that doesn't exist. To complete your move specify one that does.")
            if int(get_amount(session)) > int(session['attributes']['state'][int(intent['slots']['Selection']['value']) - 1]) or int(get_amount(session)) < 1:
                return error_response(session, "You can't perform that move.", "You can't increase the number in a group, reduce it below zero or keep it the same.")
            if intent['slots']['Selection']['value'] == 1:
                if is_reduce_move():
                    a -= int(get_amount(session))
                else:
                    a = int(get_amount(session))
            elif intent['slots']['Selection']['value'] == 2:
                if is_reduce_move():
                    b -= int(get_amount(session))
                else:
                    b = int(get_amount(session))
            elif intent['slots']['Selection']['value'] == 3:
                if is_reduce_move():
                    c -= int(get_amount(session))
                else:
                    c = int(get_amount(session))
            return alexa_full_turn(session, [a, b, c])
        else:
            if int(intent['slots']['Selection']['value']) < 1 or int(intent['slots']['Selection']['value']) > 3:
                return error_response(session, "That group doesn't exist. Please choose a different one.", "You choose a group that doesn't exist. To complete your move specify one that does.")
            else:
                attributes = build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], intent['slots']['Selection']['value'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], session['attributes']['instruction_point'], session['attributes']['email'])
                return simple_response(attributes, "Finish your turn", "You haven't specified where to take that from. It's still you're turn.", "Tell me where to take that from.", False)
    elif name == "SetAmountIntent":
        a = int(session['attributes']['state'][0])
        b = int(session['attributes']['state'][1])
        c = int(session['attributes']['state'][2])
        if selection_present(session):
            if int(session['attributes']['selection']) < 1 or int(session['attributes']['selection']) > 3:
                return error_response(session, "That group doesn't exist. Please choose a different one.", "You choose a group that doesn't exist. To complete your move specify one that does.")
            if int(intent['slots']['Amount']['value']) > int(session['attributes']['state'][int(get_selection(session)) - 1]) or int(intent['slots']['Amount']['value']) < 1:
                return error_response(session, "You can't perform that move.", "You can't increase the number in a group, reduce it below zero, or keep it the same.")
            if int(get_selection(session)) == 1:
                a = int(intent['slots']['Amount']['value'])
            elif int(get_selection(session)) == 2:
                b = int(intent['slots']['Amount']['value'])
            elif int(get_selection(session)) == 3:
                c = int(intent['slots']['Amount']['value'])
            return alexa_full_turn(session, [a, b, c])
        else:
            attributes = build_attributes(session['attributes']['type'], intent['name'], intent['slots']['Amount']['value'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], session['attributes']['instruction_point'], session['attributes']['email'])
            return simple_response(attributes, "Finish your turn", "You haven't specified where to take that from. It's still you're turn.", "Tell me where to take that from.", False)
    elif name == "ReduceAmountIntent":
        a = int(session['attributes']['state'][0])
        b = int(session['attributes']['state'][1])
        c = int(session['attributes']['state'][2])
        if selection_present(session):
            if int(session['attributes']['selection']) < 1 or int(session['attributes']['selection']) > 3:
                return error_response(session, "That group doesn't exist. Please choose a different one.", "You choose a group that doesn't exist. To complete your move specify one that does.")
            if int(intent['slots']['Amount']['value']) > int(session['attributes']['state'][int(get_selection(session)) - 1]) or int(intent['slots']['Amount']['value']) < 1:
                return error_response(session, "You can't perform that move.", "You can't increase the number in a group, reduce it below zero, or keep it the same.")
            if int(get_selection(session)) == 1:
                a -= int(intent['slots']['Amount']['value'])
            elif int(get_selection(session)) == 2:
                b -= int(intent['slots']['Amount']['value'])
            elif int(get_selection(session)) == 3:
                c -= int(intent['slots']['Amount']['value'])
            return alexa_full_turn(session, [a, b, c])
        else:
            attributes = build_attributes(session['attributes']['type'], intent['name'], intent['slots']['Amount']['value'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], session['attributes']['instruction_point'], session['attributes']['email'])
            return simple_response(attributes, "Finish your turn", "You haven't specified where to take that from. It's still you're turn.", "Tell me where to take that from.", False)
    elif name == "ReduceMoveIntent":
        if int(intent['slots']['Selection']['value']) < 1 or int(intent['slots']['Selection']['value']) > 3:
            return error_response(session, "That group doesn't exist. Please choose a different one.", "You choose a group that doesn't exist. To complete your move specify one that does.")
        if int(intent['slots']['Amount']['value']) > int(session['attributes']['state'][int(intent['slots']['Selection']['value']) - 1]) or int(intent['slots']['Amount']['value']) < 1:
                return error_response(session, "You can't perform that move.", "You can't increase the number in a group, reduce it below zero, or keep it the same.")
        a = int(session['attributes']['state'][0])
        b = int(session['attributes']['state'][1])
        c = int(session['attributes']['state'][2])
        if int(intent['slots']['Selection']['value']) == 1:
            a -= int(intent['slots']['Amount']['value'])
        elif int(intent['slots']['Selection']['value']) == 2:
            b -= int(intent['slots']['Amount']['value'])
        elif int(intent['slots']['Selection']['value']) == 3:
            c -= int(intent['slots']['Amount']['value'])
        return alexa_full_turn(session, [a, b, c])
    elif name == "SetMoveIntent":
        if int(intent['slots']['Selection']['value']) < 1 or int(intent['slots']['Selection']['value']) > 3:
            return error_response(session, "That group doesn't exist. Please choose a different one.", "You choose a group that doesn't exist. To complete your move specify one that does.")
        if int(intent['slots']['Amount']['value']) > int(session['attributes']['state'][int(intent['slots']['Selection']['value']) - 1]) or int(intent['slots']['Amount']['value']) < 1:
                return error_response(session, "You can't perform that move.", "You can't increase the number in a group, reduce it below zero, or keep it the same.")
        a = int(session['attributes']['state'][0])
        b = int(session['attributes']['state'][1])
        c = int(session['attributes']['state'][2])
        if int(intent['slots']['Selection']['value']) == 1:
            a = int(intent['slots']['Amount']['value'])
        elif int(intent['slots']['Selection']['value']) == 2:
            b = int(intent['slots']['Amount']['value'])
        elif int(intent['slots']['Selection']['value']) == 3:
            c = int(intent['slots']['Amount']['value'])
        return alexa_full_turn(session, [a, b, c])
    elif name == "InstructionsIntent" or name == "AMAZON.HelpIntent":
        return simple_response(build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], 0, session['attributes']['email']), "Nim instructions", "You have opened the instructions. Use next and previous to navigate and resume to go back to your game.", "Use next and previous to navigate and resume to go back to your game.", False)
    elif name == "AMAZON.CancelIntent" or name == "AMAZON.StopIntent":
        return simple_response({}, "Thanks for playing", "Please play again.", None, True)
    elif name == "AMAZON.YesIntent":
        if session['attributes']['state'][0] == 0 and session['attributes']['state'][1] == 0 and session['attributes']['state'][2] == 0:
            return new_game(session)
        else:
            return simple_response(keep_attributes(session), "You can't do that", "You cannot perform that operation right now. Continue playing.", "A mistake is no reason to give up, keep on playing.", False)
    elif name == "AMAZON.NoIntent":
        if session['attributes']['state'][0] == 0 and session['attributes']['state'][1] == 0 and session['attributes']['state'][2] == 0:
            return simple_response({}, "Thanks for playing", "Please play again.", None, True)
        else:
            return simple_response(keep_attributes(session), "You can't do that", "You cannot perform that operation right now. Continue playing.", "A mistake is no reason to give up, keep on playing.", False)
    elif name == "ChangeSettingsIntent":
        return simple_response(build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], "easy", session['attributes']['instruction_point'], session['attributes']['email']), "Your turn", "I'll go easy on you next time. It's still your turn.", "Next time I'll go easy on you. You still need to finsih this game or start a new one.", False)
    elif name == "AMAZON.RepeatIntent":
        if session['attributes']['instruction_point'] == "None":
            a = session['attributes']['state'][0]
            b = session['attributes']['state'][1]
            c = session['attributes']['state'][2]
            return simple_response(keep_attributes(session), "Your turn", "I've made my move. The game is " + str(a) + ", " + str(b) + ", " + str(c) + ".", "The game is " + str(a) + ", " + str(b) + ", " + str(c) + ". Make a move.", False)
        else:
            return simple_response(keep_attributes(session), "Instructions part " + session['attributes']['instruction_point'] , get_instruction_part(int(session['attributes']['instruction_point'])), "You can continue what you're doing.", False)
    elif name == "AMAZON.StartOverIntent":
        return new_game(session)
    elif name == "StartIntent":
        return new_game(session)
    elif name == "AMAZON.NextIntent":
        if session['attributes']['instruction_point'] == "None":
            return simple_response(keep_attributes(session), "You can't do that", "You cannot perform that operation right now. Continue playing.", "A mistake is no reason to give up, keep on playing.", False)
        elif int(session['attributes']['instruction_point']) == 7:
             return simple_response(build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], 0, session['attributes']['email']), "Instructions start", get_instruction_part(0), "Use next to continue.", False)
        else:
            return simple_response(build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], int(session['attributes']['instruction_point']) + 1, session['attributes']['email']), "Instructions part " + str(int(session['attributes']['instruction_point']) + 1), get_instruction_part(int(session['attributes']['instruction_point']) + 1), "Use next to continue", False)
    elif name == "AMAZON.PreviousIntent":
        if session['attributes']['instruction_point'] == "None":
            return simple_response(keep_attributes(session), "You can't do that", "You cannot perform that operation right now. Continue playing.", "A mistake is no reason to give up, keep on playing.", False)
        elif int(session['attributes']['instruction_point']) == 1:
             return simple_response(build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], 0, session['attributes']['email']), "Instructions start", get_instruction_part(0), "Use next to continue.", False)
        elif int(session['attributes']['instruction_point']) == 0:
             return simple_response(build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], 7, session['attributes']['email']), "Instructions start", get_instruction_part(7), "Use next to continue.", False)
        else:
            return simple_response(build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], int(session['attributes']['instruction_point']) - 1, session['attributes']['email']), "Instructions part " + str(int(session['attributes']['instruction_point']) - 1), get_instruction_part(int(session['attributes']['instruction_point']) - 1), "Use next to continue.", False)
    elif name == "AMAZON.ResumeIntent":
        return simple_response(build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], "None", session['attributes']['email']), "Resumed", "You resumed the game, its your turn", "The game is " + session['attributes']['state'][0] + ", " + session['attributes']['state'][1] + ", " + session['attributes']['state'][2] + ".", False)
    elif name == "NewIntent":
        return new_game(session)
    elif name == "SetAccountIntent":
        return simple_response(build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], session['attributes']['instruction_point'], "myrpi" + str(intent['slots']['ID']['value']) + "@gmail.com"), "Updated", "I updated the destination to send game info", "It's your turn, keep on playing", False)
    else:
        raise ValueError("Invalid intent")

#utility functions

def send_email(session, game_state, mid_state):
    old_state = session['attributes']['state']
    target_email = session['attributes']['email']
    msg = MIMEMultipart()
    msg['Subject'] = "alexa nim game " + game_state[0] + " " + game_state[1] + " " + game_state[2] + " " + mid_state[0] + " " + mid_state[1] + " " + mid_state[2] + " " + old_state[0] + " " + old_state[1] + " " + old_state[2] + " " + session['sessionID']
    msg['From'] = "emailcommanddispatcher@gmail.com"
    msg['To'] = target_email
    body = "This is a message for your Raspberry Pi. You can ignore it."
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("emailcommanddispatcher@gmail.com", "sendforfree")
    text = msg.as_string()
    server.sendmail("emailcommanddispatcher@gmail.com", target_email, text)
    server.quit()

def alexa_make_a_move(state):
    xored = state[0] ^ state[1] ^ state[2]
    if xored == 0: #alexa should loose
        for i in range(3):
            if state[i] != 0:
                target = i
                number = 1
    else: #alexa should win, compute the best move
        for z in range(3):
            s = state[z] ^ xored
            if s <= state[z]:
                target = z
                number = state[z] - s
    state[target] -= number
    return state

def alexa_full_turn(session, game_state):
    if game_state == [0, 0, 0]:
        return simple_response(build_attributes(None, None, None, None, 0, 0, 0, session['attributes']['difficulty'], session['attributes']['instruction_point'], session['attributes']['email'], session, game_state), "Game over", "You won this time. Would you like to play again?", "Would you like to play again?", False)
    game_state_cache = game_state
    game_state = alexa_make_a_move(game_state)
    if game_state != [0, 0, 0]:
        return simple_response(build_attributes(None, None, None, None, game_state[0], game_state[1], game_state[2], session['attributes']['difficulty'], session['attributes']['instruction_point'], session['attributes']['email'], session, game_state_cache), "Your turn", "I made my move. Now there are " + str(game_state[0]) + ", " + str(game_state[1]) + " and " + str(game_state[2]) + " left.", "There are " + str(game_state[0]) + ", " + str(game_state[1]) + " and " + str(game_state[2]) + " left. Make a move.", False)
    else:
        return simple_response(build_attributes(None, None, None, None, 0, 0, 0, session['attributes']['difficulty'], session['attributes']['instruction_point'], session['attributes']['email'], session, game_state_cache), "Game over", "You lost this time. Would you like to play again?", "Would you like to play again?", False)

def selection_present(session):
    return session['attributes']['selection'] != "None"

def amount_present(session):
    return session['attributes']['amount'] != "None"

def get_selection(session):
    return session['attributes']['selection']

def get_amount(session):
    return session['attributes']['amount']

def is_reduce_move(session):
    return session['attributes']['type'] == "ReduceAmountIntent"

def get_state(session):
    return session['attributes']['state']

def new_game(session):
    if session['attributes']['difficulty'] == "easy":
        a = 3
        b = 5
        c = 7
    else:
        a = 3
        b = 5
        c = 6
    return simple_response(build_attributes(None, None, None, None, a, b, c, session['attributes']['difficulty'], session['attributes']['instruction_point'], session['attributes']['email'], session), "Your turn", "This is a new game. The game is " + str(a) + ", " + str(b) + ", " + str(c) + ".", "The game is " + str(a) + ", " + str(b) + ", " + str(c) + ". Make a move.", False)

def keep_attributes(session):
    return build_attributes(session['attributes']['type'], session['attributes']['lastIntent'], session['attributes']['amount'], session['attributes']['selection'], session['attributes']['state'][0], session['attributes']['state'][1], session['attributes']['state'][2], session['attributes']['difficulty'], session['attributes']['instruction_point'], session['attributes']['email'])

def get_instruction_part(number):
    if number == 0:
        return "Use next and previous to navigate and resume to go back to your game."
    elif number == 1:
        return "Nim is a two player game popular in the game theory branch of math."
    elif number == 2:
        return "The game is played with distinct groups of objects. In this game there is three."
    elif number == 3:
        return "A move consists of choosing a group and reducing the number of objects in it."
    elif number == 4:
        return "This can be done in one move or in two parts by selecting a group and number seprately."
    elif number == 5:
        return "There are two ways to affect a pile, you can set it to a lesser amount or take an amount away from it. Both are allowed."
    elif number == 6:
        return "The goal of the game is to take the last object in the game."
    elif number == 7:
        return "You can also tell me where to send emails if you use pi display. The email needs to be in the form my r pi some numer at gmail.com."

# --------------- Helpers that build all of the responses ----------------------


def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def simple_response(attributes, title, content, reprompt, should_end, session="None", mid="None"):
    if session == "None":
        return build_response(attributes, build_speechlet_response(
        title, content, reprompt, should_end))
    if mid == "None":
        mid = session['attributes']['state']
    send_email(session, attributes['state'], mid)
    return build_response(attributes, build_speechlet_response(
        title, content, reprompt, should_end))

def error_response(session, error_text, error_reprompt):
    return simple_response(keep_attributes(session), "You can't do that", error_text, error_reprompt, False)

def build_attributes(move_type, intent, amount, selection, a, b, c, difficulty, instructions, email):
    return {
    "type": str(move_type),
    "lastIntent": str(intent),
    "amount": str(amount),
    "selection": str(selection),
    "difficulty": str(difficulty),
    "instruction_point" : str(instructions),
    "email" : str(email),
    "state": [ 
        str(a),
        str(b),
        str(c)
    ]
}
