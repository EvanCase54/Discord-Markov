import discord
import markovify
import asyncio

##########
# CONFIG #
##########

# Set this to the path where your .txts are. This should be a folder that contains .txt files with the name of the chain/command
textdir = "logs/"

# A list of dictionaries, each one a markov.
# Filename is the name of the file within the above directory
# Command is the argument used for calling this markov
# Username is the name of the user (for changing nicknames). If it is set to None, it will not change the nickname
# Avatar is the file name of the avatar for this user. If it is set to None, it will not change the avatar. It looks for the avatar in the same directory as the logs
# Newline set to False if you want it to seperate sentences based on periods instead of newlines
config = [
  {
    'filename': 'text.txt',
    'command': 'text',
    'username': None,
    # Example to set the nickname:
    # 'username': 'Test User',
    'avatar': None,
    # Example to set the avatar:
    # 'avatar': 'test.png'
    'newline': True,
  }
 ]

# Default avatar name
defaultavatar = 'avatar.png'

# Bot token goes here
bottoken = "MTg3ODE4MDI4NjQwMTA4NTQ0.CrGbBQ.syQBhtEptt9mNSGcKG0O2a_sres"

# Set the commands to trigger a markov. The second one is optional
command = ".markov"
altcommand = ".mk"

################

currentavatar = defaultavatar

for c in config:
    c['model'] = None
    c['cache'] = []

def markov(model):
    m = None
    while m == None:
        m = model.make_sentence()
    return "\u200b"+m.encode("ascii","backslashreplace").decode("unicode-escape")

def markovcache():
    for c in config:

        if c['username']:
            markovname = c['username']
        else:
            markovname = c['filename'].strip('.txt')

        print("Generating cache for {0}.".format(markovname))

        while len(c['cache']) <= 10:
            m = markov(c['model'])
            c['cache'].append(m)

for c in config:
    with open(textdir+c['filename']) as t:
        text = t.read()

    if c['newline']:
        c['model'] = markovify.text.NewlineText(text)
    else:
        c['model'] = markovify.Text(text)

print("Generating markov phrases. If this takes too long, your source text may be too short.\n")
markovcache()


client = discord.Client()

async def sendmarkov(markov, message):
    if len(markov['cache']) == 0:
        markovcache()

    if markov['username']:
        markovname = markov['username']
    else:
        markovname = markov['filename'].strip('.txt')

    msg = c['cache'].pop()

    if message.channel.is_private:
        await client.send_message(message.channel, msg)
        print("PM with {0.author}\n{1}:{2}\n".format(message, markovname, msg[1:]))

    else:
        oldname = message.server.me.display_name

        if markov['username']:
            try:
               await client.change_nickname(message.server.me, markov['username'])
            except:
                print("Tried to change nickname on {0.server.name}, failed.".format(message))

        if markov['avatar'] and currentavatar != markov['avatar']:
            try:
                with open(textdir+markov['avatar']) as a:
                    avvy = a.read()
                await client.change_profile(avatar=avvy)

                currentavatar = markov['avatar']
            except:
                print("Tried to change avatar, failed.")

        elif currentavatar != defaultavatar
            try:
                with open(defaultavatar) as a:
                    avvy = a.read()
                await client.change_profile(avatar=avvy)
            except:
                pass

        await client.send_message(message.channel, msg)

        if markov['username']:
            try:
               await client.change_nickname(message.server.me, oldname)
            except:
                pass

        print("{0.server.name}#{0.channel.name}\n{1}:{2}\n".format(message, markovname, msg[1:]))

    markovcache()

@client.event
async def on_ready():
    print('Logged in as:\n{0.name}, {0.id}\n'.format(client.user))
    with open(defaultavatar) as a:
        avvy = a.read()
    await client.change_profile(avatar=avvy)

@client.event
async def on_message(message):
    if message.author.bot or message.author == client.user:
        return

    if message.content.lower().split()[0] == command or message.content.lower().split()[0] == altcommand:

        if len(config) == 1:
            await sendmarkov(config[0], message)
            return

        if len(message.content.split()) > 1:
            arg = message.content.lower().split()[1]

            for c in config:
                if c['command'] == arg:
                    await sendmarkov(c, message)
                    return

client.run(bottoken)
