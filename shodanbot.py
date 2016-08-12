#!/usr/bin/env python

import os
import time
from slackclient import SlackClient
import shodan


# starterbot's ID as an environment variable
#BOT_ID = os.environ.get("BOT_ID")
BOT_ID = "INSERT YOUR BOT ID"
SLACK_BOT_TOKEN = "INSERT YOUR SLACK BOT TOKEN"

SHODAN_TOKEN = "INSERT YOUR SHODAN API TOKEN"

# constants
AT_BOT = "<@" + BOT_ID + ">:"
EXAMPLE_COMMAND = "do"

# instantiate Slack & Twilio clients
slack_client = SlackClient(SLACK_BOT_TOKEN)
shodan_client = shodan.Shodan(SHODAN_TOKEN)


def handle_command(command, channel, user):

    print '{0} submitted command "{1}"'.format(user, command)

    response = "Command not found." # default response

    if (command.find('scan')!=-1):
        return return_response("Command is not supported, sorry!", channel)

    if command.startswith('commands'):
        response = "```"
        response += shodan_header()
        response += "```"
        response += """
	Welcome to ShodanBot! 
	Supported commands are: 
	*commands* - You found it! 
	*manifesto* - Print the Hacker's Manifesto 
	*search <terms>* - search Shodan for <terms> 
	\t Filters are not supported. Sorry.
        *resolve <host>* - Resolve a host with Shodan
        *host <host>* - See what Shodan knows about <host>
	"""

    if command.startswith('manifesto'):
        response = "```"
        response += hackers_manifesto() 
	response += "```"

    if command.startswith('host'):
        addr = command[len('host '):] 

        try:
            host = shodan_client.host(addr)
	except shodan.exception.APIError as e:
            print "API Error: {0}".format(e)
            return return_response("Invalid query", channel)

        # Print general info
        response = """
        IP: %s
        Organization: %s
        Operating System: %s
        """ % (host['ip_str'], host.get('org', 'n/a'), host.get('os', 'n/a'))

        # Print all banners
        for item in host['data']:
            response = """
                Port: %s
                Banner: %s
            """ % (item['port'], item['data'])

    if command.startswith('resolve'):
        item = command[len('resolve'):]
        results = shodan_client.search(item)

        response = results

    if command.startswith('search'):
        item = command[len('search'):]

	try:
            results = shodan_client.search(item)
        except shodan.exception.APIError as e:
            print "API Error: {0}".format(e)
            return return_response("Invalid query", channel)

        detail = 'Results found: %s \n' % results['total'] 
        for result in results['matches']:
            for host in result['hostnames']:
                detail += 'Host: %s ' % host

            detail += 'IP Addr: %s \n' % result['ip_str']

        response = detail

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def return_response(response,channel):
    return slack_client.api_call("chat.postMessage", channel=channel,
	text=response,
        as_user=True)

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel'], output['user']
    return None, None, None

def hackers_manifesto():
    return """==Phrack Inc.==

                    Volume One, Issue 7, Phile 3 of 10

=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
The following was written shortly after my arrest...

                       \/\The Conscience of a Hacker/\/

                                      by

                               +++The Mentor+++

                          Written on January 8, 1986
=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

        Another one got caught today, it's all over the papers.  "Teenager
Arrested in Computer Crime Scandal", "Hacker Arrested after Bank Tampering"...
        Damn kids.  They're all alike.

        But did you, in your three-piece psychology and 1950's technobrain,
ever take a look behind the eyes of the hacker?  Did you ever wonder what
made him tick, what forces shaped him, what may have molded him?
        I am a hacker, enter my world...
        Mine is a world that begins with school... I'm smarter than most of
the other kids, this crap they teach us bores me...
        Damn underachiever.  They're all alike.

        I'm in junior high or high school.  I've listened to teachers explain
for the fifteenth time how to reduce a fraction.  I understand it.  "No, Ms.
Smith, I didn't show my work.  I did it in my head..."
        Damn kid.  Probably copied it.  They're all alike.

        I made a discovery today.  I found a computer.  Wait a second, this is
cool.  It does what I want it to.  If it makes a mistake, it's because I
screwed it up.  Not because it doesn't like me...
                Or feels threatened by me...
                Or thinks I'm a smart ass...
                Or doesn't like teaching and shouldn't be here...
        Damn kid.  All he does is play games.  They're all alike.

        And then it happened... a door opened to a world... rushing through
the phone line like heroin through an addict's veins, an electronic pulse is
sent out, a refuge from the day-to-day incompetencies is sought... a board is
found.
        "This is it... this is where I belong..."
        I know everyone here... even if I've never met them, never talked to
them, may never hear from them again... I know you all...
        Damn kid.  Tying up the phone line again.  They're all alike...

        You bet your ass we're all alike... we've been spoon-fed baby food at
school when we hungered for steak... the bits of meat that you did let slip
through were pre-chewed and tasteless.  We've been dominated by sadists, or
ignored by the apathetic.  The few that had something to teach found us will-
ing pupils, but those few are like drops of water in the desert.

        This is our world now... the world of the electron and the switch, the
beauty of the baud.  We make use of a service already existing without paying
for what could be dirt-cheap if it wasn't run by profiteering gluttons, and
you call us criminals.  We explore... and you call us criminals.  We seek
after knowledge... and you call us criminals.  We exist without skin color,
without nationality, without religious bias... and you call us criminals.
You build atomic bombs, you wage wars, you murder, cheat, and lie to us
and try to make us believe it's for our own good, yet we're the criminals.

        Yes, I am a criminal.  My crime is that of curiosity.  My crime is
that of judging people by what they say and think, not what they look like.
My crime is that of outsmarting you, something that you will never forgive me
for.

        I am a hacker, and this is my manifesto.  You may stop this individual,
but you can't stop us all... after all, we're all alike.

                               +++The Mentor+++"""

def shodan_header():
    return """
  .--.--.     ,---,                                                      ,---,.               ___     
 /  /    '. ,--.' |                    ,---,                           ,'  .'  \            ,--.'|_   
|  :  /`. / |  |  :       ,---.      ,---.'|                   ,---, ,---.' .' |   ,---.    |  | :,'  
;  |  |--`  :  :  :      '   ,'\     |   | :               ,-+-. /  ||   |  |: |  '   ,'\   :  : ' :  
|  :  ;_    :  |  |,--. /   /   |    |   | |   ,--.--.    ,--.'|'   |:   :  :  / /   /   |.;__,'  /   
 \  \    `. |  :  '   |.   ; ,. :  ,--.__| |  /       \  |   |  ,"' |:   |    ; .   ; ,. :|  |   |    
  `----.   \|  |   /' :'   | |: : /   ,'   | .--.  .-. | |   | /  | ||   :     \'   | |: ::__,'| :    
  __ \  \  |'  :  | | |'   | .; :.   '  /  |  \__\/: . . |   | |  | ||   |   . |'   | .; :  '  : |__  
 /  /`--'  /|  |  ' | :|   :    |'   ; |:  |  ," .--.; | |   | |  |/ '   :  '; ||   :    |  |  | '.'| 
'--'.     / |  :  :_:,' \   \  / |   | '/  ' /  /  ,.  | |   | |--'  |   |  | ;  \   \  /   ;  :    ; 
  `--'---'  |  | ,'      `----'  |   :    :|;  :   .'   \|   |/      |   :   /    `----'    |  ,   /  
            `--''                 \   \  /  |  ,     .-./'---'       |   | ,'                ---`-'   
                                   `----'    `--`---'                `----'                           
"""

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
	print shodan_header()
        print("ShodanBot connected and running!")
        while True:
            command, channel, user = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel, user)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

