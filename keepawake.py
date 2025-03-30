from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def main():
    return "Bot is awake"

def run():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    server = Thread(target=run)
    server.start()

# In your main bot file:
# keep_alive()  # Uncomment this line to keep the bot alive on Replit
# client.run('MTM1NTMwMDU2NzMzNzE0MDI4NQ.GthCI5.Tw1ZOgg28JgcbJw1JnDo98WFZdF36l99rqqROU')
