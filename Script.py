from __future__ import print_function
import enum
import os.path
from random import randrange
from discord import client
from googleapiclient.discovery import build
import gspread
from gspread.models import Spreadsheet
from gspread_dataframe import set_with_dataframe
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from httplib2 import Response
import pandas as pd
import numpy as np
import json
import discord
from discord.ext import commands
import logging
import pygsheets
import time
import datetime
import random
#imports all needed packages
pyg = pygsheets.authorize(client_secret='credentials.json') #Inits the pygsheets api
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
#Creates a log for the discord bot, good for debugging
# If modifying these scopes, delete the file token.json. (The end user (In this case You charlie, shouldn't have to do that because i'm not changing the scope unless i have to later))
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
# The ID and range of a sample spreadsheet.
with open('details.json') as f:
    data = json.load(f) 

URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['googleSheetId'],
    data['workSheetName']
)
InvestorsURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['InvestersID'],
    data['Investorssheetgid']
)
SSaccessURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['SSaccessID'],
    data['SSaccessgid']
)
UserListURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['UserListID'],
    data['UserListgid']
)
RPOInfoURL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&gid={1}'.format(
    data['RPOinfoID'],
    data['RPOinfogid']
)  #these make the URLS needed for pandas to read the needed CSVs, in combination with the details.json file
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

service = build('sheets', 'v4', credentials=creds)
Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all') #Creates the data fram for investors
RPOlist = list() #initializes empty list for list of RPOs with investments
spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0)

def updateInvestors():
    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=data['Master_SPREADSHEET_ID'],
                            range=data['Master_RANGE_NAME']).execute()
    values = result.get('values', [])
    #Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
    Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all') #Creates the data frame for investors
    RPOlist = list() #initializes empty list for list of RPOs with investments
    spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0)
    spreadoutsdf2 = pd.read_csv(SSaccessURL)
    for row in values:
        RPOlist.append(row[0]) #Adds all RPOs with investments to a list
    #print(RPOlist)
    for i in RPOlist:
        Investmentsdf.loc[i].dropna()#removes all placeholder/non investment rows
        print(Investmentsdf.loc[i])
    for i in RPOlist:
        try:
            #print(i)
            spreadoutsdf.loc[i]
        except:
            newRPO = i
            newsheetID = input('Input sheet ID for new RPO ' + newRPO + " ") #gets sheetID from user for new RPO
            newgid1 = input('Input GID1 for new RPO ' + newRPO + " ") #gets gid for tab1 from user for new RPO
            newgid2 = input('Input GID2 for new RPO ' + newRPO + " ") #gets gid for tab2 from user for new RPO
            newrpoDict = {'rpo': [newRPO],'sheetID': [newsheetID], 'gid1': [newgid1], 'gid2': [newgid2]} #creates a dictionary to transform into a dataframe to add to the list of sheets and use to add to the persistent list of them
            spreadoutsdf = spreadoutsdf.append(pd.DataFrame(data=newrpoDict).set_index('rpo')) #adds new RPO info to the list of sheets
            spreadoutsdf2 = spreadoutsdf2.append(pd.DataFrame(data=newrpoDict)) #adds new RPO info to the list of sheets for sending to permanent storage
            # ACCES GOOGLE SHEET
            gc = gspread.service_account(filename='service_account.json') #gets credentials
            sh = gc.open_by_key(data['SSaccessID']) #gets sheetinfo
            worksheet = sh.get_worksheet(7) #-> 0 - first sheet, 1 - second sheet etc. 
            # APPEND DATA TO SHEET
            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
            set_with_dataframe(worksheet, spreadoutsdf2) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
    return RPOlist

def portfolio(rpo):
    if rpo == 'EXMPL':
        return
    else:
        Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
        Investmentsdf = pd.read_csv(InvestorsURL, index_col=0) #Creates the data frame for investors
        spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0) #creates the data frame that we reference to get the info needed to push stuff to spreadsheets
        df = pd.DataFrame(Investmentsdf.loc[rpo]) #creates the data frame with the specific investments with just one rpo
        df = df.reset_index() #fixes the data frame so it can be concatenated with with the market value data frame
        Marketdf = Marketdf.reset_index() #fixes the data frame so it can be concatenated with the specific investments data frame
        df = pd.concat([df, Marketdf], axis = 1).dropna(axis=0).rename(columns={rpo:'Shares'}) #concatenates the two dataframes, removes private companies, and fixes a column title
        df['Market Value'] = df['Shares'] * df['Market Price']  #does the math to make the market value column
        sum = df['Market Value'].sum() #Gets the sum of the stock prices



        request = service.spreadsheets().values().get(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'], range='Visuals!C32:C40', majorDimension = 'COLUMNS', valueRenderOption = 'UNFORMATTED_VALUE')
        response = request.execute()
        history = response['values']
        history = [ item for elem in history for item in elem]
        history.append(sum)
        history.insert(0, sum)
        history = np.array(history)
        history = history.astype(float)
        minimum = min(history)*0.8
        maximum = max(history)*1.2
        minmax = [minimum, maximum] #these lines do stuff to get the min and max values for the line graph
        history = [str(round(x,2)) for x in history]
        history = list(history)
        print(rpo)
        batch_update_values_request_body = {
            "value_input_option" : 'USER_ENTERED',  # How the input data should be interpreted.
            "data": [
                {"range": 'A11:E44',
                "majorDimension":'COLUMNS',
                "values": [
                    df['Shares'].tolist(),
                    df['Symbol'].tolist(),
                    df['Market Price'].tolist(),
                    df['Day change'].tolist(),
                    df['Market Value'].tolist()]},#Converts dataframe into the form needed to send to google sheets
                {"range": 'E4',
                "majorDimension":'COLUMNS',
                "values":[[sum]]
                },
                {"range": 'Visuals!C30:C40',
                "majorDimension":'COLUMNS',
                "values":[history]
                },
                {"range": 'Visuals!A14:A15',
                "majorDimension":'COLUMNS',
                "values":[minmax]
                }
                ]#Prepares full list of values that need to be sent to the spreadsheet 
        }
        request = service.spreadsheets().values().batchUpdate(spreadsheetId=spreadoutsdf.loc[rpo, 'sheetID'], body=batch_update_values_request_body)
        response = request.execute() #updates spreadsheet

userList = pd.read_csv(UserListURL, index_col=0) 
#print(userList.head())
#bot stuff here:
bot = commands.Bot(command_prefix='$') #this sets the prefix, needed to tell the bot what messages to look at, for now its set to `$`, this can change later
def mods():
    with open('mods.json') as m: #the mods.json file contains the userIDs of the mods helping manage the project, and charlie
        modList = json.load(m)['Mods']
    return modList

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        """if message.author.id == 406885177281871902:
            if message.channel == 687817008355737606:
                await message.channel.send('Message from {0.author}: {0.content}'.format(message))
        else:"""
        if message.channel.id == 687817008355737606 or message.channel.id == 893867549589131314:
            if message.embeds != None:
                if message.author.id == 406885177281871902:
                        embeds = message.embeds # return list of embeds
                        for embed in embeds:
                            try:
                                content = embed.to_dict()['description'] # Pulls out message content of embed
                                amount = content.split()[-2]
                            except: 
                                print(embed.to_dict())
                                return
                            try:
                                amount = int(''.join(filter(str.isdigit, amount)))
                                user = content[:(content.find('#')+5)].strip()
                                print(content, user, user in pd.read_csv(UserListURL)['Author'].astype(str).to_list())
                                if user in pd.read_csv(UserListURL)['Author'].astype(str).to_list():
                                    df3 = pd.read_csv(UserListURL)
                                    df3['new'] = df3['Author']
                                    df3 = df3.set_index('new')
                                    df3.loc[user, 'Coin Amount'] = str(amount*5)
                                    df3['userID'] = df3['userID'].astype(str)
                                    #print(df3.head())
                                    #df3.drop(columns=['new'])
                                    gc = gspread.service_account(filename='service_account.json') #gets credentials
                                    sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                                    worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                                    # APPEND DATA TO SHEET
                                    #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                                    set_with_dataframe(worksheet, df3) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                                else:
                                    print()
                            except:
                                return
                #print(message.content)
                if message.content.startswith('$joinRPO'):
                    author = message.author
                    userid = author.id
                    RPO  = message.content.split()[-1].upper()
                    if RPO not in pd.read_csv(RPOInfoURL, index_col=0, usecols=['FULL NAME', 'TAG', 'Account Balance'])['TAG'].astype(str).to_list(): #makes sure RPO trying to be joined exists
                        await message.channel.send("<:KSplodes:896043440872235028> Error: RPO " +RPO + " is not a registered RPO")
                        return
                    elif str(userid) in pd.read_csv(UserListURL)['userID'].astype(str).to_list(): #makes sure user isn't already in an RPO
                        await message.channel.send("<:KSplodes:896043440872235028> Error: You are already in an RPO: " + pd.read_csv(UserListURL, index_col=0).loc[userid, 'RPO'])
                        return
                    elif str(userid) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
                        rpo = RPO
                        newUser = {'userID':[str(userid)], 'RPO':RPO, 'Author':[author], 'Coin Amount': [0], 'lastWorkAmount': [0], 'lastWork': [0], 'lastDaily': [0]}
                        df = pd.DataFrame(newUser).set_index('userID')
                        df2 = pd.DataFrame(newUser)
                        userList = pd.read_csv(UserListURL, index_col=0).append(pd.DataFrame(newUser))
                        userListOutput = pd.read_csv(UserListURL).append(df2)
                        userListOutput['userID'] = userListOutput['userID'].astype(str)
                        gc = gspread.service_account(filename='service_account.json') #gets credentials
                        sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                        worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                        # APPEND DATA TO SHEET
                        #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                        set_with_dataframe(worksheet, userListOutput) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                        print("<@!"+str(message.author.id) + "> you are now in RPO " + str(newUser['RPO'][0]))
                        name = message.author.display_name
                        await message.author.edit(nick=name+" ["+str(rpo)+"]")
                        await message.channel.send("<@!"+str(message.author.id) + "> you are now in RPO " + rpo)
                elif message.content.startswith('$updatePortfolios'):
                    if message.author not in mods():
                        return
                    sheet = service.spreadsheets()
                    result = sheet.values().get(spreadsheetId=data['Master_SPREADSHEET_ID'],
                        range=data['Master_RANGE_NAME']).execute()
                    values = result.get('values', [])
                    #Marketdf = pd.read_csv(URL, index_col=0, usecols=['Symbol', 'Market Price', 'Day change']).dropna(axis=0) #Creates the dataframe (think spreadsheet, but in a more manipulatable manner) for stock prices
                    Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all') #Creates the data frame for investors
                    RPOlist = list() #initializes empty list for list of RPOs with investments
                    spreadoutsdf = pd.read_csv(SSaccessURL, index_col=0)
                    spreadoutsdf2 = pd.read_csv(SSaccessURL)
                    for row in values:
                        RPOlist.append(row[0]) #Adds all RPOs with investments to a list
                    #print(RPOlist)
                    for i in RPOlist:
                        portfolio(i)
                    await message.channel.send("Portfolio's updated!")
                elif message.content.startswith('$updateInvestors'):
                    if message.author not in mods():
                        return
                    updateInvestors()
                    await message.channel.send("Investors's updated!")
                elif message.content.startswith('$work'):
                    isAllowed = False
                    allowedids = ['837812373451702303','837812586997219372','837812662116417566','837812728801525781','837812793914425455','400445639210827786','685331877057658888','337743478190637077','837813262417788988','338173415527677954','253752685357039617']
                    for id in allowedids:
                        if discord.utils.get(message.guild.roles, id=int(id)) in message.author.roles:
                            isAllowed = True
                        else:
                            isAllowed
                    if isAllowed:
                        df = pd.read_csv(UserListURL)
                        df['userID'] = df['userID'].astype(str)
                        df['new'] = df['userID']
                        df = df.set_index('new')
                        lastWork = df.loc[str(message.author.id), 'lastWork']
                        currentUse = time.mktime(message.created_at.timetuple())
                        timeDifference = currentUse - lastWork
                        if timeDifference < 43200:
                            await message.channel.send("<:KSplodes:896043440872235028> Error: **" + message.author.display_name + "** You need to wait " + str(datetime.timedelta(seconds=43200-timeDifference)) + " more to use this command.")
                        elif timeDifference > 43200:
                            df.loc[str(message.author.id), 'lastWork'] = currentUse
                            amount = random.randrange(250, 600, 5) #generates random number from 250 to 600, in incrememnts of 5 (same as generating a radom number between 40 and 120, and multiplying it by 5)
                            lastamount = int(df.loc[str(message.author.id), 'lastWorkAmount'])
                            df.loc[str(message.author.id), 'Coin Amount'] += lastamount
                            df.loc[str(message.author.id), 'lastWorkAmount'] = amount
                            embeddict = {'color': 6345206, 'type': 'rich', 'description': message.author.display_name + ', you started working again. You gain '+ str(lastamount) +' <:HotTips2:465535606739697664> from your last work. Come back in **12 hours** to claim your paycheck of '+ str(amount) + ' <:HotTips2:465535606739697664> and start working again with `$work`'}
                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                            sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                            worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                            # APPEND DATA TO SHEET
                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                            set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                            await message.channel.send(embed=discord.Embed.from_dict(embeddict))
                    elif isAllowed == False:
                        return
                elif message.content.startswith('$daily'):
                    isAllowed = False
                    for role in ['225414319938994186','225414600101724170','225414953820094465','377254753907769355','338173415527677954','253752685357039617']:
                        if discord.utils.get(message.guild.roles, id=int(role)) in message.author.roles:
                            isAllowed = True
                        else:
                            isAllowed
                    if isAllowed:
                        df = pd.read_csv(UserListURL)
                        df['userID'] = df['userID'].astype(str)
                        df['new'] = df['userID']
                        df = df.set_index('new')
                        lastWork = df.loc[str(message.author.id), 'lastDaily']
                        currentUse = time.mktime(message.created_at.timetuple())
                        timeDifference = currentUse - lastWork
                        if timeDifference < 86400:
                            await message.author.send("<:KSplodes:896043440872235028> Error: **" + message.author.display_name + "** You need to wait " + str(datetime.timedelta(seconds=86400-timeDifference)) + " more to use this command.")
                        elif timeDifference > 86400:
                            df.loc[str(message.author.id), 'lastDaily'] = currentUse
                            amount = 1500 #assigned number for daily
                            df.loc[str(message.author.id), 'Coin Amount'] += amount
                            embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+str(message.author.id) +'>, here is your daily reward: 1500 <:HotTips2:465535606739697664>'}
                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                            sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                            worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                            # APPEND DATA TO SHEET
                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                            set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                            await message.author.send(embed=discord.Embed.from_dict(embeddict))
                    elif isAllowed == False:
                        return
                elif message.content.startswith('$editCoins'): #takes two args: <userID>, the user and an signed integer <int>, positive, or negative. if negative, and the value is larger than the value of funds attached to the user, sets the funds amount to 0 
                    isAllowed = False
                    for role in [338173415527677954,253752685357039617,225413350874546176]:
                        if discord.utils.get(message.guild.roles, id=int(role)) in message.author.roles:
                            isAllowed = True
                        else:
                            isAllowed
                    if isAllowed:
                        args = message.content.split()
                        if int(args[-1]) == 0:
                            embeddict = {'color': 6345206, 'type': 'rich', 'description': '<:KSplodes:896043440872235028> Error: Cannot Add or Remove 0 funds.'}
                            await message.channel.send(embed=discord.Embed.from_dict(embeddict))
                        elif int(args[-1]) > 0:
                            df = pd.read_csv(UserListURL)
                            df['userID'] = df['userID'].astype(str)
                            df['new'] = df['userID']
                            df = df.set_index('new')
                            df.loc[str(message.mentions[0].id), 'Coin Amount'] += abs(int(args[-1]))
                            embeddict = {'color': 6345206, 'type': 'rich', 'description': '✅' + str(abs(int(args[-1]))) +'<:HotTips2:465535606739697664> has been given to <@!' + str(message.mentions[0].id) + '>'}
                            await message.channel.send(embed=discord.Embed.from_dict(embeddict))
                        elif int(args[-1]) < 0:
                            df = pd.read_csv(UserListURL)
                            df['userID'] = df['userID'].astype(str)
                            df['new'] = df['userID']
                            df = df.set_index('new')
                            df.loc[str(message.mentions[0].id), 'Coin Amount'] -= min(df.loc[str(message.mentions[0].id), 'Coin Amount'], abs(int(args[-1])))
                            embeddict = {'color': 6345206, 'type': 'rich', 'description': '✅' + str(min(df.loc[str(message.mentions[0].id), 'Coin Amount'], abs(int(args[-1])))) +'<:HotTips2:465535606739697664> has been removed from <@!' + str(message.mentions[0].id) + '>'}
                            await message.channel.send(embed=discord.Embed.from_dict(embeddict))
                        else:
                            await message.channel.send('<:KSplodes:896043440872235028> Error: unrecognized or missing arguments.')
                            return
                        gc = gspread.service_account(filename='service_account.json') #gets credentials
                        sh = gc.open_by_key(data['UserListID']) #gets sheetinfo
                        worksheet = sh.get_worksheet(8) #-> 0 - first sheet, 1 - second sheet etc. 
                        # APPEND DATA TO SHEET
                        #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                        set_with_dataframe(worksheet, df) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                elif message.content.startswith('$coins'):
                    if message.mentions == []:
                        df = pd.read_csv(UserListURL, index_col=0)
                        funds = df.loc[message.author.id, 'Coin Amount']
                        embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+ str(message.author.id) + '> has ' + str(funds) + '<:HotTips2:465535606739697664>'}
                        await message.author.send(embed=discord.Embed.from_dict(embeddict))
                    elif message.mentions != []:
                        df = pd.read_csv(UserListURL, index_col=0)
                        funds = df.loc[message.mentions[0].id, 'Coin Amount']
                        embeddict = {'color': 6345206, 'type': 'rich', 'description': '<@!'+ str(message.mentions[0].id) + '> has ' + str(funds) + '<:HotTips2:465535606739697664>'}
                        await message.author.send(embed=discord.Embed.from_dict(embeddict))
                elif message.content.startswith('$buyShares'): #args: <Coins/Funds>, <Symbol>, <Amount> 
                    if message.channel.id != 687817008355737606:
                        return
                    author = message.author
                    userid = author.id
                    args = message.content.split()
                    if str(userid) not in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
                        await message.channel.send("<:KSplodes:896043440872235028> Error: Not registered in an RPO for the bot. Please register with the bot through $joinRPO <RPO_Tag>")
                        return
                    elif str(userid) in pd.read_csv(UserListURL)['userID'].astype(str).to_list():
                        Investmentsdf = pd.read_csv(InvestorsURL, index_col=0).dropna(axis=1, how='all')
                        await message.channel.send("Investing for: " + pd.read_csv(UserListURL, index_col=0).loc[userid,'RPO'])
                        if not pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'hasInvested']:
                            sheet = pyg.open_by_key(pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'sheetID'])
                            sheet.share("", role='reader', type='anyone')
                            SSaccess = pd.read_csv(SSaccessURL)
                            SSaccess['new'] = SSaccess['rpo']
                            SSaccess = SSaccess.set_index('new')
                            SSaccess.loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'hasInvested'] = True
                            gc = gspread.service_account(filename='service_account.json') #gets credentials
                            sh = gc.open_by_key(data['SSaccessID']) #gets sheetinfo
                            worksheet = sh.get_worksheet(7) #-> 0 - first sheet, 1 - second sheet etc. 
                            # APPEND DATA TO SHEET
                            #your_dataframe = pd.DataFrame(data=newrpoDict) #creates DF to export new sheet info to persisten storage 
                            set_with_dataframe(worksheet, SSaccess) #-> THIS EXPORTS YOUR DATAFRAME TO THE GOOGLE SHEET
                        await message.author.send('Link to Investment sheet: https://docs.google.com/spreadsheets/d/{0}'.format(pd.read_csv(SSaccessURL, index_col=0).loc[pd.read_csv(UserListURL, index_col=0).loc[message.author.id, 'RPO'], 'sheetID']))
                        userList = pd.read_csv(UserListURL)
                        userList["new"] = userList['UserID']
                        userList = userList.set_index("new")

                        

with open('bottoken.json') as t:
    token = json.load(t)['Token']

client = MyClient()
client.run(token)