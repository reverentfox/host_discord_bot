from dotenv import load_dotenv 
import os
hf_token_id = os.environ['TOKEN']

from gradio_client import Client
from PIL import Image
import os
import shutil
import discord

cwd = os.getcwd()
client = Client("https://reverent-atlei.hf.space/",hf_token=hf_token_id)

async def send_message(message, user_message, is_private):
    try:
        if message.attachments:
            try:
                image = message.attachments[0]
                image_url = image.url
            except IndexError:
                pass
        else:
            image_url = ''
        
        async with message.channel.typing():
            text_output,image_location = client.predict(
				user_message,	# str  in 'message' Textbox component
				image_url,	# str (filepath or URL to image) in 'Upload any Image' Image component
				api_name="/predict"
            )
            if text_output == "there ya go!":
                shutil.copy(image_location,cwd+'/img.png')
                os.remove(image_location)
                await message.channel.send(file=discord.File('img.png'))

        if "\n\n" in text_output:
          
          output_list = text_output.split("\n\n")
          
          for i in range(len(output_list)):
            await message.author.send(output_list[i]) if is_private else await message.channel.send(output_list[i])
        else:
           await message.author.send(text_output) if is_private else await message.channel.send(text_output)
        
    except Exception as e:
        print(e)

def run_discord_bot():
    intents = discord.Intents.default()
    intents.message_content = True
    client = discord.Client(intents=intents)

    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)

        if user_message[0] == '?':
            user_message = user_message[1:]
            await send_message(message, user_message, is_private=True)
        else:
            await send_message(message, user_message, is_private=False)

    discord_token = os.environ['DISCORD_TOKEN']
    client.run(discord_token)

if __name__ == '__main__':
    run_discord_bot()
