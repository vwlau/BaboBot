import discord
from discord.ext import commands
import asyncio
import json

#TOKEN = 'NDU0MTA4Mjk5MzU3NTg1NDI4.DgYRzw.qR4Sz16nN8RA-wvnROt3d2tAUvU'

def config_load():

    with open('config.json', 'r', encoding='utf-8') as read_config:
        return json.load(read_config)

config = config_load()

bot = commands.Bot(command_prefix = '%')

@bot.event
async def on_ready():
    print('Bot is ready.')

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    #adds guilds and channels to the db if they are not yet in the db at bot start
    for guild in bot.guilds:                                    #for each guild
        #print('Guild ' + str(guild))
        if str(guild.id) not in db:                             #if not in the db
            db[str(guild.id)] = {}                              #add entry for guild in db
        for channel in guild.text_channels:                     #for each guild's channels
            if str(channel.id) not in db[str(guild.id)]:        #if not in db
                db[str(guild.id)][str(channel.id)] = False      #add sub-entry for channel in guild's entry
                                                                #default listen state is False
    #print(json.dumps(db, indent = 4))

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

#checks each message for a URL in an embed in the listened to channels
@bot.event
async def on_message(message):
    #ignores bot users
    if (message.author.bot): #message.author == bot.user this would be ignore self
        return

    current_channel = message.channel

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    #Find if this channel is anonymous
    anon = False
    if db[str(message.guild.id)][str(message.channel.id)] == 'a':
        anon = True

    #get link dump channel
    #only looks for link dump channel in current message's guild
    dump_channel = None
    for channel in db[str(message.guild.id)]:
        if db[str(message.guild.id)][channel] == 'd':
            dump_channel = bot.get_channel(int(channel))

    #Find if this channel is listening
    listening = False
    if db[str(message.guild.id)][str(message.channel.id)] == True:
        listening = True

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)


    if(anon and message.content.startswith('%direct')):
        return
    elif(anon):
        await message.delete()
        if(len(message.content)==0 and len(message.attachments) > 0):
            for attach in message.attachments:
                #await current_channel.send(attach)
                await current_channel.send('( ͡° ͜ʖ ͡°).jpg')
        elif(len(message.attachments) > 0):
            await current_channel.send(message.content)
            for attach in message.attachments:
                #await current_channel.send(attach)
                await current_channel.send('( ͡° ͜ʖ ͡°).jpg')
        else:
            await current_channel.send(message.content)

    #quick check to see if its worth waiting for an embed
    if(
    message.content.find('http') != -1 or
    message.content.find('www') != -1 or
    message.content.find('.co') != -1 or
    message.content.find('.org') != -1 or
    message.content.find('.net') != -1
    ):
        #sets how long to wait for an embed to pop up
        await asyncio.sleep(5)

    #checks for embeds and puts some restrictions on what channels are allowed
    if(
    dump_channel != None and                            #dump channel exists
    listening and                                       #listening to current channel
    len(message.embeds) > 0                             #embeds exists
    #current_channel != dump_channel and
    #and not current_channel.is_nsfw()
    ):
        for embeds in message.embeds:
            await dump_channel.send(str(message.author) + ' posted in #' + str(current_channel) + ' ' + embeds.url)

    #allows commands to still work
    await bot.process_commands(message)

#deletes and reposts anonymous messages
'''@bot.event
async def on_message(message):
    #ignores bot users
    if (message.author.bot): #message.author == bot.user this would be ignore self
        return

    current_channel = message.channel

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    #allows commands to still work
    await bot.process_commands(message)'''

#send message for unrecongized commands
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('I\'m sorry, Dave. I\'m afraid I can\'t do that.')

#adds guild and it's channels to db on guild join, similar to on ready
@bot.event
async def on_guild_join(guild):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    db[str(guild.id)] = {}

    for channel in guild.text_channels:
        db[str(guild.id)][str(channel.id)] = False

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    #print(json.dumps(db, indent = 4))

#removes guild and it's channels to db on guild remove
@bot.event
async def on_guild_remove(guild):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    db.pop(str(guild.id), None)

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    #print(json.dumps(db, indent = 4))

#adds channel to guild's entry in db on channel creation
@bot.event
async def on_guild_channel_create(channel):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    db[str(channel.guild.id)][str(channel.id)] = False

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    #print(json.dumps(db, indent = 4))

#removes channel from guild's entry in db on channel deletion
@bot.event
async def on_guild_channel_delete(channel):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    db[str(channel.guild.id)].pop(str(channel.id), None)

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    #print(json.dumps(db, indent = 4))

#a test ping pong command
@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

#set a channel to be listened to
@bot.command(pass_context = True)
async def listen(ctx, desig_chan : discord.TextChannel = None):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    if desig_chan is None:       #If a channel is not specified
        desig_chan = ctx.channel #defaults to channel command was typed in

    if db[str(ctx.guild.id)][str(desig_chan.id)] == 'd':
        await ctx.send('Cannot listen to the link dump channel!')
    elif db[str(ctx.guild.id)][str(desig_chan.id)] == 'a':
        await ctx.send('Cannot listen to the anonymous channel!')
    elif db[str(ctx.guild.id)][str(desig_chan.id)] == False:
        db[str(ctx.guild.id)][str(desig_chan.id)] = True
        await ctx.send('Now listening to \'{}\'.'.format(desig_chan.name))
    else:
        await ctx.send('Already listening to \'{}\''.format(desig_chan.name))

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    #print(json.dumps(db, indent = 4))

#set a channel to be ignored
@bot.command(pass_context = True)
async def ignore(ctx, desig_chan : discord.TextChannel = None):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    if desig_chan is None:       #If a channel is not specified
        desig_chan = ctx.channel #defaults to channel command was typed in

    if db[str(ctx.guild.id)][str(desig_chan.id)] == True:
        db[str(ctx.guild.id)][str(desig_chan.id)] = False
        await ctx.send('Now ignoring \'{}\'.'.format(desig_chan.name))
    elif db[str(ctx.guild.id)][str(desig_chan.id)] == 'a':
        db[str(ctx.guild.id)][str(desig_chan.id)] = False
        await ctx.send('Was an anonymous channel. Now ignoring \'{}\'.'.format(desig_chan.name))
    elif db[str(ctx.guild.id)][str(desig_chan.id)] == 'd':
        await ctx.send('Already ignoring \'{}\' because it is the link dump channel.'.format(desig_chan.name))
#    elif db[str(ctx.guild.id)][str(desig_chan.id)] == 'a':
#        await ctx.send('Already ignoring \'{}\' because it is the anonymous channel.'.format(desig_chan.name))
    else:
        await ctx.send('Already ignoring \'{}\'.'.format(desig_chan.name))

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    #print(json.dumps(db, indent = 4))

#set a channel to be link dump
@bot.command(pass_context = True)
async def dump(ctx, desig_chan : discord.TextChannel = None):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    if desig_chan is None:       #If a channel is not specified
        desig_chan = ctx.channel #defaults to channel command was typed in

    old_ch = ''
    num_dumps = 0

    for channel in db[str(ctx.guild.id)]:
        if db[str(ctx.guild.id)][channel] == 'd':
            num_dumps += 1
            old_ch = channel
            old_ch_name = bot.get_channel(int(old_ch)).name #finds the channel name from the id string

    if num_dumps == 1 and db[str(ctx.guild.id)][str(desig_chan.id)] != 'd':
        db[str(ctx.guild.id)][old_ch] = False
        db[str(ctx.guild.id)][str(desig_chan.id)] = 'd'
        await ctx.send('There can only be one link dump channel!\n\'{}\' was the old link dump channel and is now set to ignore.\n\'{}\' is now the link dump channel.'.format(old_ch_name, desig_chan.name))
    elif db[str(ctx.guild.id)][str(desig_chan.id)] == 'd':
        await ctx.send('\'{}\' is already the link dump channel!'.format(desig_chan.name))
    else:
        db[str(ctx.guild.id)][str(desig_chan.id)] = 'd'
        await ctx.send('\'{}\' is now the link dump channel'.format(desig_chan.name))

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    #print(json.dumps(db, indent = 4))

@bot.command(pass_context = True)
async def anon(ctx, desig_chan : discord.TextChannel = None):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    if desig_chan is None:       #If a channel is not specified
        desig_chan = ctx.channel #defaults to channel command was typed in

    if db[str(ctx.guild.id)][str(desig_chan.id)] == 'd':
        await ctx.send('Cannot anonymize the link dump channel!')
    elif db[str(ctx.guild.id)][str(desig_chan.id)] == True:
        await ctx.send('Cannot anonymize a listened channel!')
    elif db[str(ctx.guild.id)][str(desig_chan.id)] == False:
        db[str(ctx.guild.id)][str(desig_chan.id)] = 'a'
        await ctx.send('Now anonymizing \'{}\'.'.format(desig_chan.name))
    else:
        await ctx.send('Already anonymizing \'{}\''.format(desig_chan.name))

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    #print(json.dumps(db, indent = 4))

#set a channel to be revealed
'''@bot.command(pass_context = True)
async def reveal(ctx, desig_chan : discord.TextChannel = None):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    if desig_chan is None:       #If a channel is not specified
        desig_chan = ctx.channel #defaults to channel command was typed in

    if db[str(ctx.guild.id)][str(desig_chan.id)] == 'a':
        db[str(ctx.guild.id)][str(desig_chan.id)] = False
        await ctx.send('\'{}\' has been revealed! It is now set to ignore.'.format(desig_chan.name))
    elif db[str(ctx.guild.id)][str(desig_chan.id)] == 'd':
        await ctx.send('Reveal command cannot change state of \'{}\' because it is the link dump channel.'.format(desig_chan.name))
    else:
        await ctx.send('\'{}\'is already revealed because it is an ignored channel.'.format(desig_chan.name))

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)'''

    #print(json.dumps(db, indent = 4))


#gives an embed showing the channel states
@bot.command(pass_context = True)
async def info(ctx):

    with open('db.json', 'r') as read_db:
        db = json.load(read_db)

    dump = ''
    anon = ''
    listened =''
    ignored = ''

    for channel in db[str(ctx.guild.id)]:
        if db[str(ctx.guild.id)][channel] == 'd':
            dump += str(bot.get_channel(int(channel))) + '\n'
        elif db[str(ctx.guild.id)][channel] == 'a':
            anon += str(bot.get_channel(int(channel))) + '\n'
        elif db[str(ctx.guild.id)][channel] == True:
            listened += str(bot.get_channel(int(channel))) + '\n'
        else:
            ignored += str(bot.get_channel(int(channel))) + '\n'

    with open('db.json', 'w') as write_db:
        json.dump(db, write_db)

    if len(dump) == 0:
        dump = 'None'
    if len(anon) == 0:
        anon = 'None'
    if len(listened) == 0:
        listened = 'None'
    if len(ignored) == 0:
        ignored = 'None'

    embed = discord.Embed(title = 'Server Listen State Information',
    description = 'Lists of the listen state of all the channels in the server',
    color = discord.Color.dark_blue())

    embed.add_field(name = 'Link Dump Channel', value = dump, inline = True)
    embed.add_field(name = 'Anonymous Channel(s)', value = anon, inline = True)
    embed.add_field(name = 'Listened Channel(s)', value = listened, inline = True)
    embed.add_field(name = 'Ignored Channel(s)', value = ignored, inline = True)

    await ctx.send(embed=embed)

#removes the default help command
bot.remove_command('help')

#custom help command showing what commands the bot has, what they do, and how to use them
@bot.command(pass_context = True)
async def help(ctx):

    embed = discord.Embed(title = 'HELP!',
    description = 'Available commands for Jeffe',
    color=discord.Color.gold())

    embed.add_field(name = '%ping', value = 'Pong!', inline = False)
    embed.add_field(name = '%info', value = 'Tells you the listen state of each channel.', inline = False)
    embed.add_field(name = '%dump <channel>', value = 'Designates a link dump channel. There can only be one. Defaults to the channel it was typed in.', inline = False)
    embed.add_field(name = '%anon <channel>', value = 'Designates an anonymous channel. Defaults to the channel it was typed in.', inline = False)
    embed.add_field(name = '%listen <channel>', value = 'Designates channel to be monitored for links. Defaults to the channel it was typed in.', inline = False)
    embed.add_field(name = '%ignore <channel>', value = 'Designates a channel to be ignored. Defaults to the channel it was typed in.', inline = False)

    embed.set_footer(text = 'My name is Jeffe.')

    await ctx.send(embed=embed)

bot.run(config['token'])
