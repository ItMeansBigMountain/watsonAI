import watson
import discord
from discord.utils import get
import json
from discord.ext import commands
import datetime
import os

import time

import statistics

from pprint import pprint



'''
# we create user model in:
  # def on_ready
  # def on_member_join
  # def on_message ----->   IF  there is a bug with user key in json
  # def on_raw_message_delete  ----->   IF  there is a bug with user key in json
  # def on_invite_create  ----->   IF  there is a bug with user key in json

  # HINT
  # ctrl + f ---> "date_created"  to find where all the models are

# we create settings json in
  on_ready
  on_message (keyerror)

each message in the message log has text AI sentiment data 
data set allows 'for a how does that make you feel' variable


'''



# Discord Settings
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix='//', intents=intents)

# IBM LOGIN
ai_Login = watson.login()


# default server settings
default_settings = {
  "saveMessages": False,
  'amount_until_calc' : 5,
  'delete_on_remove' : False,
  'discreet_invite' : False,
  'track_deleted_messages' : True,
}

#TODO settings not implemented yet (create setting.json if statments ) then add to setting commands
delete_on_remove = False
discreet_invite = False
track_deleted_messages = True



# IBM functions
def ai_to_Text(message):
  response = watson.analyzeText(ai_Login, message.content)
  response = json.loads(response)

  # MAKE A DICTIONARY THAT HOLDS THE AVERAGES OF THE OUTPUT
  # after saving the averages, refer to the message_Dictionary to get a total avg of all messages user sent

  emotion = response['emotion']['document']['emotion'] #dict
  entities = response['entities'] #list
  keywords = response['keywords'] #list
  relations = response['relations'] #list
  semantic_roles = response['semantic_roles'] #list
  sentiment = response['sentiment'] #dict
  concepts = response['concepts'] #list
  categories = response['categories'] #list
  # syntax = response['syntax'] #dict
  # warnings = response['warnings']


  # clean data
  clean_relations = []
  for r in relations:
    # print(r['sentence'])
    for a in r['arguments']:
      for e in a['entities']:
        clean_relations.append(  (e['type'] , e['text'])  )

  # wowowowowoww
  lolz = [ (e['type'] , e['text']) for r in relations for a in r['arguments'] for e in a['entities'] ]

  model = {
    'overall_emotion' : emotion,
    'relations' : clean_relations,
    'sentiment' :  sentiment['document']['label']  ,
    'entities' : [  (  i['text'] , i['type']  , i['sentiment']['label']  ) for i in entities  ],
    'keywords' : [  (  i['text'] , i['sentiment']['label']   ) for i in keywords  ],
    'subjects' : [  (  i['subject']['text'] , i['action']['verb']['tense'] ) for i in semantic_roles  ],
    'concepts' : [  i['label']  for i in categories  ],
  }

  # pprint(model)


  return model


# calculations
def averages_calc(userJSON , settings):
  print("\n\ncalculating {}...".format(userJSON['username']))

  # dict_keys   ['overall_emotion', 'relations', 'subjects', 'entities', 'keywords', 'concepts']
  text_Models = [ i['text_ai'] for i in userJSON['message_log']]


  # initialization of all model points through one loop
  overallEmotion = {
    'anger': [],
    'disgust': [],
    'fear': [],
    'joy': [],
    'sadness': []
  }
  allRelations = []
  allSentiments = []
  allEntities = []
  allKeywords = []
  allConcepts = []
  allSubjects = []
  for i in text_Models:
    # OVERALL EMOTION
    overallEmotion['anger'].append(i['overall_emotion']['anger'])
    overallEmotion['disgust'].append(i['overall_emotion']['disgust'])
    overallEmotion['fear'].append(i['overall_emotion']['fear'])
    overallEmotion['joy'].append(i['overall_emotion']['joy'])
    overallEmotion['sadness'].append(i['overall_emotion']['sadness'])
    # relations
    for r in i['relations']:
      allRelations.append(r)
    # sentiment
    allSentiments.append(i['sentiment'])
    # entities
    for e in i['entities']:
      allEntities.append(e)
    # keywords
    for k in i['keywords']:
      allKeywords.append(k)
    # keywords
    for l in i['concepts']:
      allConcepts.append(l)
    # subject
    for s in i['subjects']:
      allSubjects.append(s)




  # OVER ALL EMOTION AVERAGE
  averageEmotion = {
    'Anger' :  sum(overallEmotion['anger']) / len(overallEmotion['anger'])   ,
    'Disgust': statistics.mean(overallEmotion['disgust']),
    'Fear': statistics.mean(overallEmotion['fear']),
    'Joy': statistics.mean(overallEmotion['joy']),
    'Sadness': statistics.mean(overallEmotion['sadness']),
    'timeCalculated' : str(datetime.datetime.now())
  }
  # CURRENT AVERAGE CALCULATION
  if len(userJSON['overallMessageEmotion_arr']) > 0:
    cur_anger = [i['Anger'] for i in userJSON['overallMessageEmotion_arr']]
    cur_disgust = [i['Disgust']  for i in userJSON['overallMessageEmotion_arr']  ]
    cur_fear = [i['Fear']  for i in userJSON['overallMessageEmotion_arr']  ]
    cur_joy = [i['Joy']  for i in userJSON['overallMessageEmotion_arr']  ]
    cur_sadness = [i['Sadness']  for i in userJSON['overallMessageEmotion_arr']  ]
    
    userJSON['overallMessageEmotion_current'] = {
      'Anger' :  statistics.mean(cur_anger)   ,
      'Disgust': statistics.mean(cur_disgust),
      'Fear': statistics.mean(cur_fear) ,
      'Joy': statistics.mean(cur_joy) ,
      'Sadness': statistics.mean(cur_sadness) ,
      'timeCalculated' : str(datetime.datetime.now())
    }
  # del overallEmotion #optional

  userJSON['overallMessageEmotion_arr'].append( averageEmotion  )

  # print('\n\n-------- emotion avg ---------')
  # pprint(  userJSON['overallMessageEmotion_current'] )






  # RELATIONS 
  relationsfrequencies = {}
  for item in allRelations:
      if item[0] in relationsfrequencies:
          relationsfrequencies[item[0]].append(item[1])
      else:
          relationsfrequencies[item[0]] = [ item[1] ]

  # dump relations in userJSON

  for x in relationsfrequencies.keys():
    if x in userJSON['relations']:
      userJSON['relations'][x].extend(relationsfrequencies[x])
    else:
      userJSON['relations'][x] = relationsfrequencies[x]

  # print('\n\n-------- relations ---------')
  # pprint(userJSON['relations'])





  # sentiment
  sentiment_frequencies = {}
  for item in allSentiments:
      if item in sentiment_frequencies:
          sentiment_frequencies[item] += 1
      else:
          sentiment_frequencies[item] = 1
  
  # dump sentiment in userJSON
  for x in sentiment_frequencies.keys():
    if x in userJSON['sentiment']:
      userJSON['sentiment'][x] += sentiment_frequencies[x]
    else:
      userJSON['sentiment'][x] = sentiment_frequencies[x]

  # print('\n\n-------- sentiment ---------')
  # pprint( userJSON['sentiment'])





  # NOTE checks if entities and keywords have duplicates
  removes = []
  if len(allEntities) > 0 and len(allKeywords) > 0:
    keywords_Length = len(allKeywords)
    for x in range(len(allEntities)):
      for y in range(keywords_Length):
        if allEntities[x][0] == allKeywords[y][0]:
          removes.append(allKeywords[y])
    # remove the item and handle key error if duplicates of multiples
    if len(removes) > 0:
      for y in removes:
        try:
          allKeywords.remove(y)
        except ValueError:
          pass
        except:
          print('\n\n################## ERROR in calculations ##################\n\n')



  # entities
  entityfrequencies = {}
  for item in allEntities:
      if item[2] in entityfrequencies:
          entityfrequencies[item[2]].append(  ( item[0] , item[1])  )
      else:
          entityfrequencies[item[2]] = [ ( item[0] , item[1])  ] 

  # dump entities in userJSON
  for x in entityfrequencies.keys():
    if x in userJSON['entities']:
      userJSON['entities'][x].extend(entityfrequencies[x])
    else:
      userJSON['entities'][x] = entityfrequencies[x]

  # print('\n\n-------- entities ---------')
  # pprint(userJSON['entities'])
  
  



  # keywords
  #  i['text'] , i['sentiment']['label'] , i['emotion'] 
  keywordfrequencies = {}
  for item in allKeywords:
      if item[1] in keywordfrequencies:
          keywordfrequencies[item[1]].append(item[0])
      else:
          keywordfrequencies[item[1]] = [item[0]]

  # dump keywords in userJSON
  for x in keywordfrequencies.keys():
    if x in userJSON['keywords']:
      userJSON['keywords'][x].extend(keywordfrequencies[x])
    else:
      userJSON['keywords'][x] = keywordfrequencies[x]
      
  # print('\n\n-------- keywords ---------')
  # pprint(userJSON['keywords'])



  # Concepts
  # # i['label']
  allConcepts = set(allConcepts) 
  conceptfrequencies = {}
  for x in allConcepts:
    x = x.split("/")[1:]
    if x[0] in conceptfrequencies:
      if len(x[1:]) > 0:
        conceptfrequencies[x[0]].append( x[1:] )
    else:
      conceptfrequencies[x[0]] = [ x[1:]  ]

  # dump concepts in userJSON
  for x in conceptfrequencies.keys():
    if x in userJSON['concepts']:
      userJSON['concepts'][x].extend(conceptfrequencies[x])
    else:
      userJSON['concepts'][x] = conceptfrequencies[x]

  # print('\n\n-------- concepts ---------')
  # pprint(userJSON['concepts'])





  # subjects
    #  i['subject']['text'] , i['action']['verb']['tense']
  subjectsfrequencies = {}
  for item in allSubjects:
      if item[1] in subjectsfrequencies:
          subjectsfrequencies[item[1]].append(item[0])
      else:
          subjectsfrequencies[item[1]] = [item[0]]

  # dump sentiment in userJSON
  for x in subjectsfrequencies.keys():
    if x in userJSON['subjects']:
      userJSON['subjects'][x].extend(subjectsfrequencies[x])
    else:
      userJSON['subjects'][x] = subjectsfrequencies[x]

  # print('\n\n-------- subjects ---------')
  # pprint(userJSON['subjects'])


  # CLEAN AVERAGE DATA MODELS
  # averageEmotion
  # relationsfrequencies
  # sentiment_frequencies
  # entityfrequencies
  # keywordfrequencies
  # conceptfrequencies
  # subjectsfrequencies







  # clear / archive logs
  if settings['saveMessages']:
    for x in userJSON['message_log']:
      userJSON['message_archive'].append(   (  x['message'] , x['timeCalculated']  )  ) 
  userJSON['message_log'] = []




  return userJSON






# DISCORD FUNCTIONALITY
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

    for guild in client.guilds:
      # channel = discord.get(guild.text_channels, name='join logs')
      
      # create text channel
      found = False
      for x in  guild.text_channels:
        if x.name == 'join-logs':
          found = True
          break
      if not found:
        print("Creating Join logs text channel")
        # NOTE: ADMIN ONLY PERMISSIONS
        # admin_role = get(guild.roles, name="Admin")
        # overwrites = {
        # guild.default_role: discord.PermissionOverwrite(read_messages=False),
        # guild.me: discord.PermissionOverwrite(read_messages=True),
        # admin_role: discord.PermissionOverwrite(read_messages=True)
        # }
        # await guild.create_text_channel('join-logs' , overwrites = overwrites)
        await guild.create_text_channel('join-logs')

      print('\n\n \t SERVER: ' , guild)

      # validate database JSON
      if os.path.exists('{}.json'.format(guild.id)):
        pass
      else:
        with open('{}.json'.format(guild.id) , 'a') as f:
          f.write("{}")

      # check for server settings
      if os.path.exists('{}_settings.json'.format(guild.id)):
        print("SETTINGS: created")
      else:
        with open('{}_settings.json'.format(guild.id), 'a') as f:
          # f.write('{"saveMessages": false}')
          json.dump(default_settings, f)
          print("SETTINGS:  stored")

      for member in guild.members:
        if member.bot:continue 
        # load json dict so we can verify users
        with open('{}.json'.format(guild.id) ) as json_file:
          try:
            json_decoded = json.load(json_file)
            # verify
            if str(member.id) in json_decoded:
              print( str(member)  , "<---- Previous user")
            else:
              print(member)
              # create model
              model = {
                'username': f'{member.name}#{member.discriminator}',
                'userId': member.id,
                'date_created' : str(datetime.datetime.now()),
                'overallMessageEmotion_arr': [], 
                'overallMessageEmotion_current': {}, 
                'relations' : {},
                'sentiment' : {},
                'entities' : {},
                'keywords' : {},
                'concepts' : {},
                'subjects' : {},
                'message_log' : [],
                'message_count' : 0,
                'message_archive' : [],
                'deleted_message_count' : 0,
                'deleted_messages' : [],
                'invite_count' : 0,
              }
              # save to json
              json_decoded[str(member.id)] = model
              with open('{}.json'.format(guild.id) , 'w') as json_file:
                  json.dump(json_decoded, json_file)
          # if json messed up, then clear db and then add the rest like normal 
          except json.decoder.JSONDecodeError:
            print("my g!")
            with open('{}.json'.format(guild.id) , 'w') as f:
              f.write("{}")
            # with open('{}.json'.format(guild) , '') as json_file:
            #     json.dump(json_decoded, json_file)

@client.event
async def on_message(message):
  server_id = message.guild.id

  # proccess commands
  await client.process_commands(message)



  # check if database.JSON in path
  if os.path.exists('{}.json'.format(server_id)):
    pass
  else:
    with open('{}.json'.format(server_id) , 'a') as f:
      f.write("{}")

  #if message was from bot(s), do nothing
  if message.author == client.user: return 
  if message.author.bot: return

  # anylize message and saves to json
  if len(message.content.split()) >= 3:

    try:
      ai = ai_to_Text(message)
    except Exception as e: return


    # each message will be added as a dictionary with their ai stats
    message_Dictionary = {
      # WE DO NOT NEED TO SAVE THE WHOLE AI OUTPUT. RATHER A DICTIONARY THAT HAS THE CLEAN AVG PER TEXT DATA 
      'message' : message.content,
      'text_ai' : ai,
      'timeCalculated' : str(datetime.datetime.now())
    }

    #adding data into json Database <user.json>
    try:
      with open('{}.json'.format(server_id) , 'r') as userDatabase:
        userDatabaseLoaded = json.load(userDatabase)
        user = userDatabaseLoaded[str(message.author.id)]


        # use userDatabaseLoaded as update model then dump it at the end of our calculations , per message
        # add message to users message_log
        user['message_log'].append(message_Dictionary)
        user['message_count'] += 1

        # # DEBUG
        print(user['username'] , user['message_count'])

        # check averages
        try:
          with open(f'{server_id}_settings.json', 'r') as f:
            # load server settings
            settingsJSON = json.load(f)
            if user['message_count'] >= settingsJSON['amount_until_calc']:
                  user['message_count'] = 0

                  # NLU MODULE --> averages returns new json with cleaned data -- DUMPAROONI
                  userDatabaseLoaded[str(message.author.id)] = averages_calc(user , settingsJSON)



        except FileNotFoundError:
          print("making new settings file...")
          with open(f'{server_id}_settings.json', 'a') as f:
            # f.write('{"saveMessages": false}')
            json.dump(default_settings, f)
          with open(f'{server_id}_settings.json', 'r') as f:
            settingsJSON = json.load(f)
            user['message_count'] = 0
            # averages returns new json with cleaned data
            userDatabaseLoaded[str(message.author.id)] = averages_calc(user , settingsJSON)
            await message.channel.send( user['overallMessageEmotion_current'] )




      # final dump 
      with open('{}.json'.format(server_id) , 'w') as userDatabase:
        json.dump(userDatabaseLoaded, userDatabase) 


    # catch if user not in database 
    except KeyError as e:
      print('key error ------>', e)
      model = {
        'username': f'{message.author}#{message.author.discriminator}',
        'userId': message.author.id,
        'date_created' : str(datetime.datetime.now()),
        'overallMessageEmotion_arr': [], 
        'overallMessageEmotion_current': {}, 
        'relations' : {},
        'sentiment' : {},
        'entities' : {},
        'keywords' : {},
        'concepts' : {},
        'subjects' : {},
        'message_log' : [],
        'message_count' : 0,
        'message_archive' : [],
        'deleted_message_count' : 0,
        'deleted_messages' : [],
        'invite_count' : 0,
      }
      # save message data to json
      userDatabaseLoaded[str(message.author.id)] = model
      with open('{}.json'.format(server_id) , 'w') as json_file:
        # add newest message into users json
        model['message_log'].append(message_Dictionary)
        model['message_count'] += 1
        json.dump(userDatabaseLoaded, json_file)
    
    # BUG if file corrupted clear page
    except json.decoder.JSONDecodeError:
      print( f'\nERROR: {message.guild.name} JSON resetting\n\n'  )
      # recreate the file
      with open('{}.json'.format(server_id) , 'w') as f:
        f.write("{}")


  #specific channel commands
  if (message.channel.id == 'channel id'):
    pass

  if message.content.startswith('.help'):
    await message.channel.send("HELP ME " )




# discord event functions
@client.event
async def on_member_join(member): #join logs
  print(member)
  server_id = member.guild.id
  joinLog = get(member.guild.text_channels, name="join-logs")
  if os.path.exists('{}.json'.format(server_id)):
    pass
  else:
    with open('{}.json'.format(server_id) , 'a') as f:
      f.write("{}")

  # create model
  model = {
    'username': f'{member.name}#{member.discriminator}',
    'userId': member.id,
    'date_created' : str(datetime.datetime.now()),
    'overallMessageEmotion_arr': [], 
    'overallMessageEmotion_current': {}, 
    'relations' : {},
    'sentiment' : {},
    'entities' : {},
    'keywords' : {},
    'concepts' : {},
    'subjects' : {},
    'message_log' : [],
    'message_count' : 0,
    'message_archive' : [],
    'deleted_message_count' : 0,
    'deleted_messages' : [],
    'invite_count' : 0,
  }
  # save to json
  with open('{}.json'.format(server_id) ) as json_file:
      json_decoded = json.load(json_file)
  json_decoded[str(member.id)] = model
  with open('{}.json'.format(server_id) , 'w') as json_file:
      json.dump(json_decoded, json_file)


  await joinLog.send(  f'{member} joined! \n Member count: {member.guild.member_count}' )

@client.event
async def on_member_remove(member): #join logs
  joinLog = get(member.guild.text_channels, name="join-logs")
  print(member)
  await joinLog.send(  f'{member} left... \n Member count: {member.guild.member_count}' )



@client.event
async def on_invite_create(invite): #join-logs

  # check if server database exists
  if os.path.exists('{}.json'.format(invite.guild.id)):
    pass
  else:
    with open('{}.json'.format(invite.guild.id) , 'a') as f:
      f.write("{}")


  #if message was from bot(s), do nothing
  if invite.inviter == client.user: return 
  if invite.inviter.bot: return

  user_id = invite.inviter.id

  # DEBUG
  # print(f"\n\n------ { invite.inviter }  CREATED INVITE ------")
  # print( invite.guild )
  # print( invite.channel )
  # print( invite.created_at )
  # print( invite.url ) 
  # print()
  # print( invite.approximate_member_count )
  # print( invite.approximate_presence_count )
  # print( invite.uses )
  # print( invite.code )
  # print( invite.id )
  # print( invite.max_age )
  # print( invite.max_uses )
  # print( invite.revoked )
  # print( invite.temporary )
  # print('------------------\n\n')
  
  # load / save database
  try:
    with open(f"{invite.guild.id}.json" , 'r' ) as db :
      data = json.load(db)
    data[str(user_id)]['invite_count'] += 1
    with open(f"{invite.guild.id}.json" , 'w' ) as db :
      json.dump(data, db)

    # send data to join-logs
    joinLog = get(invite.guild.text_channels, name="join-logs")
    await joinLog.send(  f"{ invite.inviter }  created an invite..." )

  # catch if user not in database 
  except KeyError as e:
    print(f"\n\n\t Error: on_invite_create(invite) \n GUILD: {invite.guild.id} \n user not in database... ")
    print(e)

    # user model
    model = {
      'username': f'{invite.inviter}',
      'userId': invite.inviter.id,
      'date_created' : str(datetime.datetime.now()),
      'overallMessageEmotion_arr': [], 
      'overallMessageEmotion_current': {}, 
      'relations' : {},
      'sentiment' : {},
      'entities' : {},
      'keywords' : {},
      'concepts' : {},
      'subjects' : {},
      'message_log' : [],
      'message_count' : 0,
      'message_archive' : [],
      'deleted_message_count' : 0,
      'deleted_messages' : [],
      'invite_count' : 0,
    }

    # save message data to json
    with open('{}.json'.format(invite.guild.id) , 'r') as json_file:
      userDatabaseLoaded = json.load(json_file)
      userDatabaseLoaded[str(invite.inviter.id)] = model
    with open('{}.json'.format(invite.guild.id) , 'w') as json_file:
      model['invite_count'] += 1
      json.dump(userDatabaseLoaded, json_file)

    # send data to join-logs
    joinLog = get(invite.guild.text_channels, name="join-logs")
    await joinLog.send(  f"{ invite.inviter }  created an invite..." )



  # anything else
  except Exception as e:
    print(f"\n\n\t Error: on_invite_create(invite) \n GUILD: {invite.guild.id}")
    print(e)

@client.event
async def on_guild_join(guild): #create json file
  server_id = guild.id

  if os.path.exists('{}.json'.format(server_id)):
    pass
  else:
    with open('{}.json'.format(server_id) , 'a') as f:
      f.write("{}")

@client.event
async def on_guild_remove(guild): #remove json file
    print('\n\nBOT LEFT ---> ' , guild)

    #remove json file of guild
    with open(f"{guild.id}_settings.json" , 'r') as settingsDB:
      data = json.load(settingsDB)
      if data['delete_on_remove']:
        os.remove(   str( guild.id ) +'.json'   )
        os.remove(   str( guild.id ) +'_settings.json'   )

@client.event
async def on_raw_message_delete(payload): #add to database
  # check if database is there
  if os.path.exists('{}.json'.format(payload.guild_id)):
    pass
  else:
    with open('{}.json'.format(payload.guild_id) , 'a') as f:
      f.write("{}")

  # add data to database
  try:
    message = payload.cached_message
    user_id = message.author.id

    # deleted message data
    deleted = {
      'time_deleted' : str(datetime.datetime.now()),
      'message' : message.content,
      'chennel' : payload.cached_message.channel.name,
    }


    #if message was from bot(s), do nothing
    if message.author == client.user: return 
    if message.author.bot: return
    


    # load / save database
    with open(f"{payload.guild_id}.json" , 'r' ) as db :
      data = json.load(db)
    data[str(user_id)]['deleted_message_count'] += 1
    data[str(user_id)]['deleted_messages'].append(   deleted    )
    with open(f"{payload.guild_id}.json" , 'w' ) as db :
      json.dump(data, db)


    # DEBUG
    print('\n\n----------------------')
    print("\t Deleted Message ")
    print('\t' ,payload.guild_id , '\n')
    print( 'Author: ' ,payload.cached_message.author.name)
    print( 'Channel: ' ,payload.cached_message.channel.name)
    print( 'Message: ' ,deleted['message'])
    print( 'Time Deleted: ' ,deleted['time_deleted'])
    print( 'Deleted Message Count' ,data[str(user_id)]['deleted_message_count'])
    # print(data[str(user_id)]['deleted_messages'])
    print("----------------------\n\n")

  # deleted message was sent when bot was turned off / not in guild
  except AttributeError:
    # print(f"\n\n\t Error: on_raw_message_delete(payload)\n GUILD: {payload.guild_id} \n Deleted a message that the bot didnt cache... ")
    return

  # catch if user not in database 
  except KeyError as e:
    print(f"\n\n\t Error: on_raw_message_delete(payload)\n GUILD: {payload.guild_id} \n user not in database... ")
    print(e)

    # user model
    model = {
      'username': f'{message.author}#{message.author.discriminator}',
      'userId': message.author.id,
      'date_created' : str(datetime.datetime.now()),
      'overallMessageEmotion_arr': [], 
      'overallMessageEmotion_current': {}, 
      'relations' : {},
      'sentiment' : {},
      'entities' : {},
      'keywords' : {},
      'concepts' : {},
      'subjects' : {},
      'message_log' : [],
      'message_count' : 0,
      'message_archive' : [],
      'deleted_message_count' : 0,
      'deleted_messages' : [],
      'invite_count' : 0,
    }

    # save message data to json
    with open('{}.json'.format(payload.guild_id) , 'r') as json_file:
      userDatabaseLoaded = json.load(json_file)
      userDatabaseLoaded[str(message.author.id)] = model
    with open('{}.json'.format(payload.guild_id) , 'w') as json_file:
      model['deleted_message_count'] += 1
      model['deleted_messages'].append(deleted)
      json.dump(userDatabaseLoaded, json_file)

  # anything else
  except Exception as e:
    print(f"\n\n\t Error: on_raw_message_delete(payload) \n GUILD: {payload.guild_id}")
    print(e)



# commands
@client.command()
async def settings(ctx):
  server_id = ctx.guild.id
  with open(f'{server_id}_settings.json', 'r') as f:
    settingsJSON = json.load(f)

  # display
  display = display_Settings(settingsJSON)
  await ctx.send(embed=display)

@client.command()
@commands.has_permissions(administrator=True)
async def message_archive(ctx):
  server_id = ctx.guild.id
  with open(f'{server_id}_settings.json', 'r') as f:
    settingsJSON = json.load(f)
  with open('{}_settings.json'.format(server_id) , 'w') as settings:
    if settingsJSON['saveMessages']:
      settingsJSON['saveMessages'] = False
    else:
      settingsJSON['saveMessages'] = True
    json.dump(settingsJSON, settings) 
  
  # display
  display = display_Settings(settingsJSON)
  await ctx.send(embed=display)

@client.command()
@commands.has_permissions(administrator=True)
async def until_calc(ctx , arg):
  try:
    print(arg)
    server_id = ctx.guild.id
    with open(f'{server_id}_settings.json', 'r') as f:
      settingsJSON = json.load(f)
    with open('{}_settings.json'.format(server_id) , 'w') as settings:
      settingsJSON['amount_until_calc'] = int(arg)
      json.dump(settingsJSON, settings) 
    
    # display
    display = display_Settings(settingsJSON)
    await ctx.send(embed=display)

  except Exception as e:
    print(e)
    await ctx.send('Make sure your argument is a number.')




# extra functions in construction
@client.event
async def on_invite_delete(invite):
    print(f"\n\n------ { invite.inviter }  DELETED INVITE ------")
    print( invite )
    print('------------------\n\n')




# custom help functions
def display_Settings(settingsJSON):
  embed = discord.Embed(title="Settings", description="Here are your settings")
  embed.add_field(name="//message_archive", value=settingsJSON['saveMessages'] , inline= False)
  embed.add_field(name="//until_calc <amount>", value=settingsJSON['amount_until_calc'] , inline= False)
  return embed






# VOICE CHAT COMMANDS
@client.event
async def on_voice_state_update(member, before, after):

  # Check for changes in voice chat
  if before.afk != after.afk:
    print(f'{after.afk = }')
  if before.channel != after.channel:
    print(f'{after.channel = }')
  if before.deaf != after.deaf:
    print(f'{after.deaf = }')
  if before.mute != after.mute:
    print(f'{after.mute = }')
  if before.self_deaf != after.self_deaf:
    print(f'{after.self_deaf = }')
  if before.self_mute != after.self_mute:
    print(f'{after.self_mute = }')
  if before.self_stream != after.self_stream:
    print(f'{after.self_stream = }')
  if before.self_video != after.self_video:
    print(f'{after.self_video = }')







@client.command()
async def join(ctx):
  channel = ctx.author.voice.channel
  vc = channel.connect()
  




@client.command()
async def leave(ctx):
  await ctx.voice_client.disconnect()











#logs into discord
client.run('')

