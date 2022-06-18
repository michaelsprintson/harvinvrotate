
# Import the os module.
from time import sleep
import re
import json
from tracemalloc import start
from discum.utils.button import Buttoner
from functools import reduce
import pickle
from dotenv import load_dotenv
import os
import numpy as np
from collections import defaultdict
import discum     
import sys

# environment variabels
ID_DICT = {"harvey":251112534231220225, "brittany": 376970858859593728}
MUDAE_ID = 432610292342587392
INPUT_NAME = sys.argv[1]

load_dotenv()
# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
scrape_channel = None

# initiate bot
bot = discum.Client(token=DISCORD_TOKEN, log=False)
inv_size = 0

# command to run on bot ready
@bot.gateway.command
def helloworld(resp):
    global scrape_channel, inv_size
    
    #run when bot ready (login)
    if resp.event.ready_supplemental: #ready_supplemental is sent after ready
        user = bot.gateway.session.user
        print("Logged in as {}#{}".format(user['username'], user['discriminator']))
    
    #autorotate all found inventorie
    if resp.event.message:
        m = resp.parsed.auto()
        if (m['author']['id'] == f"{MUDAE_ID}") and (len(m['embeds'])>0) and (m['channel_id'] == scrape_channel):
            if 'footer' in m['embeds'][0]:
                #fof given number of inventories i , click button i times and eait 5 seconds to allow picture load / mudae delay
                for i in range(0, int(m['embeds'][0]['footer']['text'].split("/")[1].strip(" ").split(" ")[0])-1):
                    #find button
                    message = bot.getMessage(m['channel_id'], m['id'])
                    data = message.json()[0]
                    buts = Buttoner(data["components"])
                    sleep(3)

                    #click button
                    bot.click(
                        data["author"]["id"],
                        channelID=data["channel_id"],
                        guildID=m['guild_id'],
                        messageID=data["id"],
                        messageFlags=data["flags"],
                        data=buts.getButton(emojiName='wright'),
                    )
                    sleep(2)
            
            #if its a pr command, grab the number of items in inventory
            elif ("Harem size:") in m['embeds'][0]['description']:
                inv_size = int(re.search("\*\*Harem size:\*\*  (?P<siz>[\d]+)  \(", m['embeds'][0]['description']).group("siz"))

        # if theres a starter inventory command, do this
        if m['content'][0:9] == "$startinv":
            # grab rotate id and channel to look for
            un_to_scrape = m['content'][10:]
            if un_to_scrape == INPUT_NAME:

                id_to_scrape = ID_DICT[un_to_scrape]
                num_of_invs = 0
                scrape_channel = m['channel_id']
                
                # scrape command
                def startscrape():
                    
                    print("about to send pr")
                    sleep(1)
                    # send pr to grab bumber of items in inventory
                    bot.sendMessage(m['channel_id'],f"$pr {id_to_scrape}")
                    num_of_invs = inv_size // 40
                    while inv_size == 0:
                        print("inv size still 0, waiting 5")
                        sleep(5)
                        #calculate the number of rotations to do
                        num_of_invs = inv_size // 40
                    print("found", num_of_invs, f"rotations needed for inv size {inv_size}")
                    # perform rotations by posting the inventory by calling mmi at rotation location and letting the command above rotate
                    for i in range(0,num_of_invs+1):
                        if i != 0:
                            bot.sendMessage(m['channel_id'],f"$mmi {id_to_scrape} ${i * 40}")
                        else:
                            bot.sendMessage(m['channel_id'],f"$mmi {id_to_scrape}")
                        print("finished rotation, watiing for next")
                        # wait 5 mins between mmi commands to let mudae timer cool down
                        sleep(605)
                while (True):
                    #run the rotator every hour
                    startscrape()
                    print("sleeping 3600")
                    sleep(3600)
            

            
 
bot.gateway.run(auto_reconnect=True)
