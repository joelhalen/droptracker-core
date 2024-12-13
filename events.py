from interactions.api.events import MessageCreate, InteractionCreate, Ready

def on_message_create(event):
    print("Message created")

def on_interaction(event):
    print("Interaction created")

def on_ready(event: Ready):
    print("Bot is ready")