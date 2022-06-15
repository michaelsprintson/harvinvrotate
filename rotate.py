
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

HARVEY_ID = 251112534231220225
MUDAE_ID = 432610292342587392

load_dotenv()
# Grab the API token from the .env file.
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
scrape_channel = None

from collections import defaultdict
import discum     
bot = discum.Client(token=DISCORD_TOKEN, log=False)
inv_size = 0

@bot.gateway.command
def helloworld(resp):
    global scrape_channel, inv_size
    
    if resp.event.ready_supplemental: #ready_supplemental is sent after ready
        user = bot.gateway.session.user
        print("Logged in as {}#{}".format(user['username'], user['discriminator']))
    
    #autorotate all found inventorie
    if resp.event.message:
        m = resp.parsed.auto()
        if (m['author']['id'] == f"{MUDAE_ID}") and (len(m['embeds'])>0) and (m['channel_id'] == scrape_channel):
            if 'footer' in m['embeds'][0]:
                for i in range(0, int(m['embeds'][0]['footer']['text'].split("/")[1].strip(" ").split(" ")[0])-1):
                    message = bot.getMessage(m['channel_id'], m['id'])
                    data = message.json()[0]
                    buts = Buttoner(data["components"])
                    # print(buts.getButton(emojiName='wright'))
                    sleep(3)
                    bot.click(
                        data["author"]["id"],
                        channelID=data["channel_id"],
                        guildID=m['guild_id'],
                        messageID=data["id"],
                        messageFlags=data["flags"],
                        data=buts.getButton(emojiName='wright'),
                    )
                    sleep(2)
            elif ("Harem size:") in m['embeds'][0]['description']:
                inv_size = int(re.search("\*\*Harem size:\*\*  (?P<siz>[\d]+)  \(", m['embeds'][0]['description']).group("siz"))

        # 
        if m['content'][0:9] == "$startinv":
            id_to_scrape = m['content'][10:]
            num_of_invs = 0
            scrape_channel = m['channel_id']
            if id_to_scrape == "":
                id_to_scrape = HARVEY_ID
            def startscrape():
                
                print("about to send pr")
                sleep(1)
                bot.sendMessage(m['channel_id'],f"$pr {id_to_scrape}")
                num_of_invs = inv_size // 40
                while inv_size == 0:
                    print("inv size still 0, waiting 5")
                    sleep(5)
                    num_of_invs = inv_size // 40
                print("found", num_of_invs, f"rotations needed for inv size {inv_size}")
                for i in range(0,num_of_invs+1):
                    if i != 0:
                        bot.sendMessage(m['channel_id'],f"$mmi {id_to_scrape} ${i * 40}")
                    else:
                        bot.sendMessage(m['channel_id'],f"$mmi {id_to_scrape}")
                    print("finished rotation, watiing for next")
                    sleep(605)
            while (True):
                startscrape()
                print("sleeping 3600")
                sleep(3600)
        

            
 
bot.gateway.run(auto_reconnect=True)
