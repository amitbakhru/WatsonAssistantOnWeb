import pandas as pd
import json
import sqlite3
import sys, os
from watson_developer_cloud import AssistantV1
from _sqlite3 import Row


##def __init__(self):
assistant = AssistantV1(username = '4cae92bc-09c2-46d4-b4c5-21fa4f2527a5',
                           password = 'A3SXrQDsAZJU',
                           version = '2018-02-16')
wrkspc_id = '49dee8c1-cd3d-43f7-9914-33cbdaace889'
##
##response = assistant.message(workspace_id = '49dee8c1-cd3d-43f7-9914-33cbdaace889')
##contxt = response['context']
a = 1
##print("****** FIRST CONTEXT *********", contxt)


def findPrinter(l_flr, l_loc):
##        print("Inside printer func 1", loc_flr)
    '''Function to read printer data from CSV file and print Watson response on screen'''
    loc_flr = l_loc.upper() + '_' + str(l_flr).upper()
    
    prdata = pd.read_csv('C:\pyfiles\printers_data.csv')
    prdata.set_index(['fac_flr'], inplace=True)
    try:
        pr_code = str(prdata.loc[loc_flr, 'printer'])
        printer_text = "I see Printer " + pr_code + " is the closest to you. \nFollowing are the instructions to set it up: \n1) Go to START menu --> Control Panel --> Printers and Devices \n2) Add Network Printer \n3) Enter " + pr_code+ " and hit ADD."
    except:
        printer_text = "Sorry, I'm unable to find a printer for that location."

##        out_text = "I see Printer " + pr_code + " is the closest to you. \nFollowing are the instructions to set it up: \n1) Go to START menu --> Control Panel --> Printers and Devices \n2) Add Network Printer \n3) Enter " + pr_code+ " and hit ADD."
##        print("Watson:", out_text)

    return(printer_text)


def getIncidentData(l_user=None, l_incno=None):
    '''Get incidents by badge ID or by specific Incident No.'''
    db_path = '/C:/pyfiles/for_watson.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    itsm_cur = conn.cursor()

    if l_incno is None:
        itsm_cur.execute('''
            SELECT * FROM itsm_data
            WHERE user = ? ''', (l_user, ))
    else:
        itsm_cur.execute('''
            SELECT * FROM itsm_data
            WHERE tckt = ? ''', (l_incno, ))

    inc_text = "Watson: Below are the last few incidents logged by you:\n"
    row = itsm_cur.fetchone()
    cnt = 0
    while row is not None and cnt < 3:
        cnt += 1
##            print(row['tckt'] + " | " + row['desc'] + " | " + row['stat'])
        inc_text += (row['tckt'] + " | " + row['desc'] + " | " + row['stat'] + "\n")
        row = itsm_cur.fetchone()
    return(inc_text)


def incNumAvailable(inc_response):
    for tag1 in inc_response["context"]:
        if tag1 == "INC":
            return(1)
    return(0)


def askChallengeQues(l_user):
    '''Get Challenge Questions by random selection for User'''
    db_path = '/C:/pyfiles/for_watson.db'
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    ques_cur = conn.cursor()
    
    ques_cur.execute('''
        SELECT * FROM user_ques
        WHERE user:=l_user AND qnum:=rnum''', 
        {"l_user":l_user, "rnum":random.randint(1,5)})
    row = ques_cur.fetchone()
    cnt = 0
    if row is not None:
        while cnt < 2:
            cnt += 1
            print("Watson: ", row['ques'])
            ans = input('User: ')
            
            if input_txt in ('quit', 'exit', 'bye', 'cancel'):
#                     print('Watson: Okay. Canceling this request')
                return_text = 'Watson: Okay. Canceling this request'
                return(0)
            elif ans != row['answ']:
                return(0)
            else:
                row = ques_cur.fetchone()
    else:
        return(0)
    
    return(1)


def processResponse(response):
    '''Function to process the response coming from Watson and call Python functions as needed'''
    print(json.dumps(response, indent=2))

    '''Return Errors if encountered'''
    for e in response["output"]["log_messages"]:
        if e["level"] == "err":
            return_text = "Error -" + e["msg"]
            return(return_text, response['context'])

    '''Display response from Watson'''
    for tag in response:
        return_text = ''
##            print(tag)
        if tag == "output":
            for txt in response["output"]["text"]:
                return_text += txt
            return(return_text, response['context'])

        if tag == "actions":
            for action in response["actions"]:
##                    print(action["name"])
                if action["name"] == "findPrinter":
                    action_text = findPrinter(response["context"]["floor_no"],
                                                   response["context"]["location"])
                    return_text += action_text
                    return(return_text, response['context'])
                
                elif action["name"] == "getIncidentData":
                    if incNumAvailable(response):
                        action_text = getIncidentData(response["context"]["user_id"],
                                                    response["context"]["INC"])
                    else:
                        action_text = getIncidentData(response["context"]["user_id"])
                    return_text += action_text
                    return(return_text, response['context'])
                
                elif action["name"] == "challenge_ques":
                    return_val = askChallengeQues(response["context"]["user_id"])
                    
                    if return_val == 1:
                        action_text = "Your password has been reset. Please check your registered personal email for new password."
                    else:
                        action_text = "Your answer did not match. Please try again later."
                    
                    return_text += action_text
                    return(return_text, response['context'])
##            else:
##                return(return_text)


def getFirstResponse(input_txt):
##        init_response = self.assistant.message(workspace_id = self.wrkspc_id,
    init_response = assistant.message(workspace_id = '49dee8c1-cd3d-43f7-9914-33cbdaace889',
                                              input = {'text':input_txt})
    response_text = processResponse(init_response)

    if response_text is None:
        response_text = "Did not get a response from Watson"

    return(response_text, init_response['context'])


def getResponse(input_txt, contxt):
    print("******* NEXT CONTEXT *******", contxt)
    next_response = assistant.message(workspace_id = '49dee8c1-cd3d-43f7-9914-33cbdaace889',
                                      input = {'text':input_txt},
##                                               context = '')
##                                              context = response['context'])
                                      context = contxt)
    response_text, contxt = processResponse(next_response)

    if response_text is None:
        response_text = "Did not get a response from Watson"
    
    return(response_text, contxt)
