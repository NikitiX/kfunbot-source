# the code is currently in horrible state, don't try to understand it.

import os,discord,json,requests,threading,time
from random import randint
from dotenv import load_dotenv
from copy import deepcopy

info = {}
dev_id = 611559561907666974
auto_dump = 90 * 60
ea_speedruns = {}
ea_messages = ['e','a','sports','it\'s in the game']
powers = [0,0,0,1,3,10]

api_dev_key = open('pbapikey.txt').read()
request = {
    'api_dev_key': api_dev_key,
    'api_user_name': 'kfunbot',
    'api_user_password': open('password.txt').read()}
response = requests.post('https://pastebin.com/api/api_login.php',data=request)
api_user_key = response.text


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

with open('sr.json') as file:
    special_responses = json.loads(file.read())

k_help = '''- k.version (k.ver)
  Displays the information about the current bot version.

- k.distraction
  Distracts you.

- k.invite
  Shows the invite link.

- k.help
  Displays this help

- k.info
  Shows the amount of registered guilds and users

the bot is now open source: https://github.com/NikitiX/kfunbot-source

'''

k_help_dev = '''- k.maintenance
  Terminates all running processes of the bot (both local and deployed)

- k.export_state
  Shows the current state JSON file.

- k.import_state
  Loads the JSON bot state.

'''

k_help_admin = '''- k.settings
  Unlocks the bot settings.
  Usage: k.settings name=value
  possible names* :
    dadbot: If the value is "true", the bot implements the features of Dad Bot.
    dadbot.reacttonickname: If the value is "true", the Dad Bot replies with "No you're not" message to the bot's guild nickname, otherwise only to 'Dad'.
    dadbot.noyourenot: If the value is "nickname", the Dad Bot says your guild nickname in "No you're not" message, otherwise if it is "username", then your username.
    specialresponses: If the value is "true", then the bot reacts to some special messages (such as "lol" -> "ok loler")
    easpeedrun: If this value is "true", then the EA Sports Intro Speedrun feature is on.

  If you type "k.settings dttm.channel" in some channel, then the channel the message is sent in would be set as the channel for the DTTM game (your progress wouldn't be lost).

  * most settings take "true" and "false" as values, unless other values are specified
  
'''

k_help_dttm = '''
--- DTTM game specific commands ---

- k.score
  Displays the current score and the guild highscore.

- k.rules
  Shows the rules of the game.

'''

k_rules_dttm = '''```--- The "Don't Touch The Mine" game rules ---
You go through the territory full of mines, counting the numbers. You can count by 1 or 2 (more requires additional limited power). If you hit the randomly generated number that is marked as "mine", you blow up and your score is reset.
Once you surpass the mine, the guild gets some amount of coins (2 for first mine, +1 for each next). Guild loses 1 coin when blowing up.
You can buy the jetpack for 200 coins to make your attack even easier.```'''

version = '''kernel's fun bot, version: `Release 1.0.0`
changes:
```DTTM:
- "power" technique to make the game easier
- guild's coins implementation
- life saver
- jetpack

the bot is now open source - https://github.com/NikitiX/kfunbot-source```'''

class Settings:
    BOOLEAN = {'true': True, 'false': False}
    def __init__(self,dict_={}):
        self.settings = dict_
    def add(self,name,vset=BOOLEAN,default='true'):
        self.settings[name] = {'value':vset[default],'set':vset}
    def set(self,name,value):
        try:
            try:
                getta = self.settings[name]['value']
            except KeyError as e:
                return str(e) + ' is not a valid property name'
            self.settings[name]['value'] = self.settings[name]['set'][value]
            return 'Succesfully changed'
        except KeyError as e:
            return str(e) + ' is not a valid value'
        except Exception as e:
            return 'unhandled error: ' + str(e)
    def get(self,name):
        try:
            return self.settings[name]['value']
        except:
            self.add(name)
            return self.settings[name]['value']
    def dict(self):
        return self.settings

async def send(channel,text):
    if randint(1,777) <= 1:
        await channel.send('<https://bit.ly/2Z2mKVA>')
    else:
        await channel.send(text)

def load_info():
    global info
    request = {
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'list',
        'api_results_limit': '100'}
    response = requests.post('https://pastebin.com/api/api_post.php',data=request)
    key = response.text.split('<paste_url>')[1].split('</paste_url>')[0].split('/')[-1]
    request = {
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'show_paste',
        'api_paste_key': key}
    response = requests.post('https://pastebin.com/api/api_post.php',data=request)
    info = json.loads(response.text)

def dump_info():
    global info
    request = {
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'list',
        'api_results_limit': '100'}
    response = requests.post('https://pastebin.com/api/api_post.php',data=request)
    key = response.text.split('<paste_url>')[1].split('</paste_url>')[0].split('/')
    request = {
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'delete',
        'api_paste_key': key}
    response = requests.post('https://pastebin.com/api/api_post.php',data=request)
    content = json.dumps(info)
    print(content)
    request = {
        'api_dev_key': api_dev_key,
        'api_user_key': api_user_key,
        'api_option': 'paste',
        'api_paste_code': content,
        'api_paste_private': '2',
        'api_paste_expire_date': 'N'}
    response = requests.post('https://pastebin.com/api/api_post.php',data=request)
    print(response.text)

def calc_fuel(difference):
    return 2 * (difference ** 2)

load_info()
print(info)

client = discord.Client()

@client.event
async def on_member_join(member):
    if member.id not in info['guilds'][str(member.guild.id)]['dnb']:
        await member.kick(reason='definitely not banned')

@client.event
async def on_message(message):
    #print(message.content,message.author.id)
    global info
    if message.author == client.user:
        return
    
    # --- k.export_state and k.import_state ---

    if message.content == 'k.export_state':
        if int(message.author.id) != dev_id:
            await send(message.channel,'Only developer can access k.export_state')
            return
        await send(message.channel,'```' + json.dumps(info) + '```\n```' + json.dumps(ea_speedruns) + '```')

    if message.content.split()[0] == 'k.import_state':
        if int(message.author.id) != dev_id:
            await send(message.channel,'Only developer can access k.export_state')
            return
        info = json.loads(' '.join(message.content.split()[1:]))
        await send(message.channel,'Done')
    
    # --- Setting up the server ---
    server_id = str(message.guild.id)
    if server_id not in info['guilds']:
        s = Settings()
        s.add('dadbot')
        s.add('dadbot.reacttonickname')
        s.add('dadbot.noyourenot',vset={'username':False,'nickname':True},default='nickname')
        s.add('specialresponses')
        s.add('easpeedrun')
        guild_info = {
            'settings': s.dict(),
            'dttm': {
                'channel': -1,
                'lastmessage_author': -1,
                'number': 0,
                'mine': randint(1,15),
                'mineseliminated': 0,
                'numberhs': 0,
                'mineseliminatedhs': 0,
                'coins': 0,
                'jetpack': {'level': 0, 'fuel': 100,'lastrecharge': time.time()},
                'ls': 0
            },
            'dnb': []
        }
        info['guilds'][server_id] = guild_info
    info['guilds'][server_id]['dttm'].setdefault('coins',0)
    info['guilds'][server_id]['dttm'].setdefault('undo',(-1,-1))
    info['guilds'][server_id]['dttm'].setdefault('jetpack', {'level': 0, 'fuel': 100, 'lastrecharge': time.time()})
    info['guilds'][server_id]['dttm'].setdefault('ls', 0)
    info['guilds'][server_id]['dnb'] = []
    s = Settings(info['guilds'][server_id]['settings'])

    # --- Setting up the user ---

    user_id = str(message.author.id)
    if user_id not in info['users']:
        user_info = {
            'name': message.author.name,
            'power': 10,
            'last_recharge': time.time()
        }
        info['users'][user_id] = user_info
    t = time.time()
    days_notrech = (t // (24 * 60 * 60)) - (info['users'][user_id]['last_recharge'] // (24 * 60 * 60))
    print(days_notrech)
    info['users'][user_id]['power'] = int(min((info['users'][user_id]['power'] + days_notrech * 10), 20))
    info['users'][user_id]['last_recharge'] = t
    

    # --- k.maintenance ---
    if message.content == 'k.maintenance':
        if int(message.author.id) != dev_id:
            await send(message.channel,'Only developer can send me into maintenance mode')
            return
        await send(message.channel,'Okay, terminating')
        dump_info()
        exit(0)

    # --- k.eval ---
    if message.content.startswith('k.eval '):
        if int(message.author.id) != dev_id:
            await send(message.channel,'Only developer can use this command')
            return
        await send(message.channel,str(eval(message.content[7:])))
    
    # --- special responses ---
    content = message.content.strip()
    if content.lower() in special_responses and s.get('specialresponses'):
        await send(message.channel,special_responses[message.content.strip().lower()])
        return

    # --- all commands with k. ---
    if content.startswith('k.'):
        command = content[2:]
        if command == 'help':
            send_message = ''
            if int(message.author.id) == dev_id:
                send_message = k_help_dev + k_help_admin + k_help
            elif message.guild.get_member(message.author.id).guild_permissions.administrator:
                send_message = k_help_admin + k_help
            else:
                send_message = k_help
            if str(message.channel.id) == info['guilds'][server_id]['dttm']['channel']:
                send_message += k_help_dttm
            send_message = '```--- Help ---\n\n' + send_message + '```'
            await send(message.channel,send_message)
            return
        if command == 'ver' or command == 'version':
            await send(message.channel,version)
            return
        if command == 'distraction':
            await send(message.channel,'https://thumbs.gfycat.com/WateryAltruisticDiplodocus-size_restricted.gif')
        if command == 'invite':
            await send(message.channel,'Invite the bot to your server: https://discord.com/api/oauth2/authorize?client_id=689072347260387385&permissions=8&scope=bot')
        if command == 'info':
            await send(message.channel,'I have ' + str(len(info['users'])) + ' registered users over ' + str(len(info['guilds'])) + ' registered guilds')

        # --- k.definitelynotban --- 
        if command.split()[0] in ('definitelynotban','dnb'):
            print('here')
            the = ' '.join(command.split()[1:])
            if the == '':
                await send(message.channel,'Please specify the user')
                return
            if the.startswith('@<') and the.endswith('>'):
                try:
                    mid = int(the[2:-1])
                    info['guilds'][server_id]['dnb'].append(mid)
                    await send(message.channel,'Definitely not banned %s' % mid)
                    for member in message.guild.members:
                        if member.id == mid:
                            await member.kick(reason='definitely not banned')
                            return
                    return
                except ValueError:
                    pass
            try:
                mid = int(the)
                info['guilds'][server_id]['dnb'].append(mid)
                await send(message.channel,'Definitely not banned %s' % mid)
                for member in message.guild.members:
                    if member.id == mid:
                        await member.kick(reason='definitely not banned')
                        return
                return
            except ValueError:
                members = message.guild.members
                result = []
                for m in members:
                    if (not m.nick is None) and (m.nick.lower().startswith(the.lower())):
                        result.append(m)
                    elif m.name.lower().startswith(the.lower()):
                        result.append(m)
                if len(result) == 0:
                    await send(message.channel,'Cannot find such a user')
                    return
                if len(result) > 1:
                    send_message = 'There were several users found: '
                    for i in result:
                        send_message += '\n- _%s#%s_' % (i.name,i.discriminator)
                    send_message += '\nPlease specify the user that you want to definitely not ban.'
                    await send(message.channel,send_message)
                    return
                if len(result) == 1:
                    mid = result[0].id
                    info['guilds'][server_id]['dnb'].append(mid)
                    await send(message.channel,'Definitely not banned %s' % mid)
                    for member in message.guild.members:
                        if member.id == mid:
                            await member.kick(reason='definitely not banned')
                            return
                    return


        
        # --- k.settings ---
        
        elif command.split()[0] == 'settings':
            if int(message.author.id) == dev_id or message.guild.get_member(message.author.id).guild_permissions.administrator:
                if command.split()[1] == 'dttm.channel':
                    info['guilds'][server_id]['dttm']['channel'] = str(message.channel.id)
                    await send(message.channel,'The DTTM game will now happen here.')
                    return
                try:
                    sname,svalue = command.split()[1].split('=')
                except:
                    await send(message.channel,'don\'t abuse the k.settings command, use k.help to know how to use it')
                    return
                response = s.set(sname,svalue)
                if response == 'Succesfully changed':
                    info['guilds'][server_id]['settings'] = s.dict()
                await send(message.channel,response)
            else:
                await send(message.channel,'Only administrators of the server or kernel can access k.settings')
                return

    # --- EA Sports Intro Speedrun ---
    if s.get('easpeedrun'):
        if message.content.strip().lower() == ea_messages[0]:
            ea_speedruns[str(message.guild.id) + '\\' + str(message.channel.id)] = {
                'state': 1,
                'start_time': time.time()}
            return
        cid = str(message.guild.id) + '\\' + str(message.channel.id)
        if cid in ea_speedruns:
            ea_info = ea_speedruns[cid]
            if message.content.strip().lower() == ea_messages[ea_info['state']]:
                ea_info['state'] += 1
                if ea_info['state'] == len(ea_messages):
                    ftime = time.time() - ea_info['start_time']
                    send_message = 'EA Sports Intro Speedrun: Your time was '
                    send_message += str(round(ftime,2))
                    send_message += ' seconds!'
                    if ftime < 2.71:
                        send_message += '\n:tada: **Congratulations!** You are faster than the narrator!'
                    await send(message.channel,send_message)
                    del ea_speedruns[cid]
                    return
            else:
                del ea_speedruns[cid]
                return

    # --- DTTM game ---
    if str(message.channel.id) == info['guilds'][server_id]['dttm']['channel']:
        dttm_info = info['guilds'][server_id]['dttm']

        # --- commands ---
        if message.content.strip() == 'k.score':
            await send(message.channel,'The current number is ' + str(dttm_info['number']) + '\nHighscore: ' + str(dttm_info['numberhs']) + '\nGuild\'s coins: ' + str(dttm_info['coins']))
            return
        if message.content.strip() == 'k.rules':
            await send(message.channel,k_rules_dttm)
            return
        if message.content.strip() == 'k.dev nextmine':
            #await send(message.channel,'don\'t dare you cheat using a debug command.')
            await send(message.channel,str(dttm_info['mine']))
            return
        if message.content.strip().split()[0] == 'k.buy':
            a = ' '.join(message.content.strip().split()[1:])
            if a == '':
                await send(message.channel,'''```Items list:
> Life saver - saves you from blowing up. One-time use.
    Cost - 15 coins
    Command - k.buy ls
> Jetpack - makes you fly longer and higher
    Cost - 200 coins
    Command - k.buy jetpack```''')
            elif a == 'ls':
                if dttm_info['coins'] < 15:
                    await send(message.channel,'Not enought money to buy **Life Saver**.')
                else:
                    info['guilds'][server_id]['dttm']['ls'] += 1
                    info['guilds'][server_id]['dttm']['coins'] -= 15
                    await send(message.channel,'Succesfully bought.')
            elif a == 'jetpack':
                if dttm_info['jetpack']['level'] == 1:
                    await send(message.channel,'**Jetpack** was already bought.')
                elif dttm_info['coins'] < 200:
                    await send(message.channel,'Not enought money to buy **Life Saver**.')
                else:
                    info['guilds'][server_id]['dttm']['jetpack']['level'] = 1
                    info['guilds'][server_id]['dttm']['coins'] -= 200
                    await send(message.channel,'Succesfully bought.')
        if message.content.strip() == 'undo':
            if info['guilds'][server_id]['dttm']['undo'] == [-1,-1,{}]:
                return
            print('here')
            if info['guilds'][server_id]['dttm']['number'] == 0 and info['guilds'][server_id]['dttm']['ls'] == 0:
                await send(message.channel,'Unfortunately, you can\'t undo after you were blown. R.I.P. your power.')
                return
            undo = info['guilds'][server_id]['dttm']['undo']
            print(undo)
            info['guilds'][server_id]['dttm'] = info['guilds'][server_id]['dttm']['undo'][2]
            info['users'][undo[0]]['power'] += powers[undo[1]]
            if info['users'][undo[0]]['power'] > 20:
                info['users'][undo[0]]['power'] = 20
            info['guilds'][server_id]['dttm']['undo'] = [-1,-1,{}]
            if info['guilds'][server_id]['dttm']['number'] == 0:
                info['guilds'][server_id]['dttm']['ls'] -= 1
            await send(message.channel,'Succesfully undone')

        # --- the game itself ---

        try:
            number = int(message.content.strip())
        except:
            return
        #if message.author.id == dttm_info['lastmessage_author']:
            #await send(message.channel,message.author.mention + ' You can\'t post twice in a row.')
            #return
        dttm_lastnumber = dttm_info['number']
        if number < dttm_lastnumber:
            await send(message.channel,message.author.mention + ' You can\'t go backwards.')
            return
        difference = number - dttm_lastnumber
        max_jetpack = len(powers) - 1
        while powers[max_jetpack] > 0:
            max_jetpack -= 1
        if info['guilds'][server_id]['dttm']['jetpack']['level'] > 0:
            i = 1
            max_jetpack += 1
            while True:
                print(calc_fuel(i))
                if calc_fuel(i) > info['guilds'][server_id]['dttm']['jetpack']['fuel']:
                    break
                i += 1
                max_jetpack += 1
        if difference >= max(len(powers),max_jetpack):
            await send(message.channel,message.author.mention + ' You can\'t perform such huge jumps.')
            return
        try:
            power = powers[difference]
        except:
            power = float('inf')
        if power != 0:
            if info['users'][user_id]['power'] < power or difference > len(powers):
                # using jetpack
                need = calc_fuel(difference - 2)
                if need > info['guilds'][server_id]['dttm']['jetpack']['fuel']:
                    await send(message.channel,message.author.mention + ''' **Not enough fuel to do that!**
Your fuel is currently %s, but you need %s fuel to perform this action. No changes were made.
''' % (info['guilds'][server_id]['dttm']['jetpack']['fuel'],need))
                else:
                    info['guilds'][server_id]['dttm']['jetpack']['fuel'] -= need
                    copy_info = deepcopy(dttm_info)
                    del copy_info['undo']
                    info['guilds'][server_id]['dttm']['undo'] = [user_id,number - dttm_lastnumber,copy_info]
                    await send(message.channel,message.author.mention + ''' **%s fuel were spent.**
You have %s fuel now. Type "undo" if you didn't want to do that.
''' % (need, info['guilds'][server_id]['dttm']['jetpack']['fuel']))
            else:
                if info['users'][user_id]['power'] < power:
                    await send(message.channel,message.author.mention + ''' **Not enough power to do that!**
    Your power is currently %s, but you need %s power to perform this action. No changes were made.
    ''' % (info['users'][user_id]['power'],power))
                    return
                else:
                    await send(message.channel,message.author.mention + ''' **%s power were spent.**
    You have %s power now. Type "undo" if you didn't want to do that.
    ''' % (power, info['users'][user_id]['power'] - power))
                    info['users'][user_id]['power'] -= power
                    print(dttm_info)
                    copy_info = deepcopy(dttm_info)
                    del copy_info['undo']
                    info['guilds'][server_id]['dttm']['undo'] = [user_id,number - dttm_lastnumber,copy_info]
        else:
            info['guilds'][server_id]['dttm']['undo'] = [-1,-1,{}]
        if number == dttm_info['mine']:
            send_message = message.author.mention + ' **You were blown!**'
            if info['guilds'][server_id]['dttm']['coins'] > 0:
                send_message += ' Guild lost 1 coin.'
                info['guilds'][server_id]['dttm']['coins'] -= 1
            send_message += '\nYour score was: ' + str(dttm_info['number']) + '\nTotal mines surpassed: ' + str(dttm_info['mineseliminated'])
            send_message += '\nIf you have a Life Saver, you can type \'undo\' to return back to the state before you were blown.'
            await send(message.channel,send_message)
            if dttm_info['number'] > dttm_info['numberhs']:
                dttm_info['numberhs'] = dttm_info['number']
                dttm_info['mineseliminatedhs'] = dttm_info['mineseliminated']
            copy_info = deepcopy(dttm_info)
            del copy_info['undo']
            dttm_info['undo'] = [user_id,number - dttm_lastnumber,copy_info]
            dttm_info['number'] = 0
            dttm_info['mine'] = randint(1,15)
            dttm_info['mineseliminated'] = 0
            dttm_info['lastmessage_author'] = -1
            info['guilds'][server_id]['dttm'] = dttm_info
            return
        else:
            dttm_info['number'] = number
        while number > dttm_info['mine']:
            await send(message.channel,message.author.mention + ' You surpassed the ' + str(dttm_info['mine']) + ' mine! Be careful for the next one!\nGuild earned %s coins.' % (dttm_info['mineseliminated'] + 2))
            dttm_info['mine'] += randint(3,15)
            dttm_info['mineseliminated'] += 1
            dttm_info['coins'] += dttm_info['mineseliminated'] + 1
        dttm_info['number'] = number
        dttm_info['lastmessage_author'] = message.author.id
        info['guilds'][server_id]['dttm'] = dttm_info
        return

    # --- Dad Bot features ---
    if s.get('dadbot'):
        nick = message.guild.get_member(client.user.id).nick
        if nick is None:
            nick = 'Dad'
        sender_nick = message.guild.get_member(message.author.id).nick
        if sender_nick is None:
            sender_nick = message.author.name
        im = None
        if content.lower().startswith('im'):
            im = content[2:]
        elif content.lower().startswith('i\'m'):
            im = content[3:]
        elif content.lower().startswith('i am'):
            im = content[4:]
        if im is None:
            return
        send_message = 'Hi%s, I\'m %s!' % (im,nick)
        if im.strip().lower() == 'dad' or (im.strip() == nick and s.get('dadbot.reacttonickname')):
            send_message = 'No you\'re not, you\'re ' + (sender_nick if s.get('dadbot.noyourenot') else message.author.name)
        await send(message.channel,send_message)

client.run(TOKEN)
