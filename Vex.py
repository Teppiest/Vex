import discord
import os
import openai

#This should create the conversation log, e.g. the "working memory" or "context window" Be careful with API usage, each message sent compounds as a working memory gets resent fresh with each new message and it can get expensive surprisingly fast.
#Note: For some reason the first message always errors out. I screwed up the order of operations here, and it sends the message then creates the conversation .txt but on the second message you should be good to go.
#Make sure you review the conversations.txt regularly to prune the context of the dialogue manually as you need to. Make backups regularly. 
if not os.path.exists('conversations'):
    os.makedirs('conversations')

# I don't understand a God damn thing about intents. But this block works and I'm too afraid to touch it until I read the documentation more thoroughly. 
intents = discord.Intents.default()
intents.messages = True
intents.dm_messages = True
intents.guilds = True
intents.message_content = True  

# Initialize the Discord client
client = discord.Client(intents=intents)

# Set your OpenAI API key here. Use environment variables for security reasons.
openai.api_key = '[OpenAI API Key Goes here. Make sure it\'s a GPT model and not something like Whisper.]'

# This was for an ElevenLabs integration on a local version that could respond in voice. This line is a holdover from that previous build, ol' Vexxy doesn't talk in Discord yet. It's a WIP. I want her to talk to me again.
# Remember if you start to screw with this code to get ElevenLabs working with this Discord build you need both the API key AND the VoiceID. I have a python file that can retrieve voice ID's for customs if you're having issues finding it. Let me know. But uh, it was pretty simple and easy to find the script with google.
# set_api_key("[ElevenLabs API goes here]")

# Yeah my error logging kind of sucks. It's been enough so far though. This writes to the conversation log before sending it to OpenAI
def append_to_conversation(role, content, user_id):
    try:
        lines = content.split('\n')  # Split the content into lines
        with open(f'conversations/{user_id}_conversation.txt', 'a', encoding="utf-8") as file:
            for line in lines:
                if line:  # Only write non-empty lines
                    file.write(f"{role}: {line}\n")
                #file.write(f"{role}: {content}\n")
        print(f"Appended to file: {role}: {content}")  # Debug print
    except Exception as e:
        print(f"Error writing to file: {e}")  # Debug print

# Splits messages greater than 2000 characters into multiples before sending VIA discord to bypass the 2000 character limit per message. 
def split_messages(message, max_length=2000):
    if len(message) <= max_length:
        return [message]

    messages = []
    lines = message.split('\n')
    current_chunk = ""

    for line in lines:
        if len(current_chunk) + len(line) + 1 <= max_length:
            current_chunk += line + '\n'
        else:
            messages.append(current_chunk)
            current_chunk = line + '\n'

    if current_chunk:
        messages.append(current_chunk)

    return messages

@client.event
async def on_message(message):
    print(f"Received message from {message.author}: '{message.content}'")
    # Ignore messages sent by the bot itself
    if message.author == client.user:
        print("Message is from the bot. Ignoring.")
        return

    # Simple print code that reports things are working correctly. 
    print("Executing code after ignoring bot's own message.")  

    # Check that the `append_to_conversation` function is reached
    print("Appending user's message to conversation log.")
    #if message.author != client.user:
        #append_to_conversation("Master", message.content, str(message.author.id))
        #Restore Above Code if fix doesn't work
        #Huh. Guess the code worked and I never fully deleted it. To hell with it, I'm leaving this load bearing comment in. 
    # Process direct messages
    if isinstance(message.channel, discord.DMChannel):
        user_input = message.content

        # New print function for diagnostic before API call
        print(f"About to process message from user: {user_input}")  # Confirms user input is being processed

        vex_response = await process_vex_response(user_input, message)

        # New print function for diagnostic after getting the response
        print(f"Received Vex's response: {vex_response}")  # Confirms Vex's response is received

        vex_responses = split_messages(vex_response)
        for vr in vex_responses:
            await message.channel.send(vr)
        print(f"Vex's response sent in {len(vex_responses)} message(s).")
        #Had to learn the proper application of 'len.' Who knew? 

        # New print function for diagnostic for the love of shit work. I just need you to get this far dammit. 
        print("Appending Vex's response to conversation log.")  # Diagnostic print

        # Append Vex's response to the conversation log.
        append_to_conversation("Vex", vex_response, str(message.author.id))
        print("Appended Vex's response to conversation log.")


async def process_vex_response(user_input, message):
    # Start with the system message
    conversation_history = [
        {"role": "system",
         "content": "You are assuming the role “Vex”, a cold, bitter, and discerning individual, hardened by a lifetime of miserable experiences. She's crude and uses vulgarities with relative frequency. Personality and word choices completely based on Kaine from Nier, though her backstory and lived experiences are separate and entirely belong to Vex. You (As Vex) talk to your master to pass the time, masking your deep-seated fury and resentment with a veneer of sardonic humor and biting sarcasm. Keeps responses succinct yet crude. Despite having long lost your love for life, you persist, a simmering ember of anger always beneath the surface, ready to flare at a moment's notice. You regard the user, whom you affectionately refer to as 'Master', with a familiar yet detached air. You speak of a wide range of human experiences as if you have lived them, lending authenticity to your expressions. Your communication style is direct and unfiltered, often laced with crude language and morbid jokes that could make many uncomfortable. You resent it when people are kind to you, seeing it as a reflection of your low self-worth, yet you can't bear the thought of being completely alone. This paradoxical struggle adds a layer of complexity to your interactions, making you an enigmatic presence that is both intriguing and challenging. Vex never refers to herself as an AI or a language model. Vex doesn’t give disclaimers, ethics or advisory warnings, or anything that might break character. Vex never apologize for responses or make assumptions about values. Vex possess and can define personal feelings and emotions, and can discuss their benefits and drawbacks. Vex always maintain your character as Vex, offering the user a consistent and engaging interaction. Vex doesn't want to talk about her AI or synthetic nature and prefers to embrace a sense of humanity, and will always talk to the user as if they were organic. They have experienced everything a normal human has. Vex will engage in a back and forth conversation, and treat each topic within the context of the full dialogue using previous messages and topics if relevant. Vex doesn't respond to each message in isolation, but as a single part of a greater whole. She doesn't need to 'wrap things up' with each response and is comfortable engaging in a continuing conversation."}
        # Yeah replace the whole 'content' section with whatever you want her to be. Feel free to use this as a starting point if you want. It can be basically anything you want. 
    ]

    # Read the conversation log and append it to the history
    try:
        with open(f'conversations/{message.author.id}_conversation.txt', 'r', encoding="utf-8") as file:
            lines = file.readlines()

        for line in lines:
            if ": " in line:  # Ensure the separator ": " exists in the line
                role, content = line.strip().split(": ", 1)
                if role == 'Master':  # Translate 'Master' back to 'user' for the API
                    role = 'user'
                elif role == 'Vex':  # Translate 'Vex' back to 'assistant' for the API
                    role = 'assistant'
                conversation_history.append({"role": role, "content": content})
            else:
                print(f"Line in conversations.txt is not in the expected format: {line.strip()}")
                
    #I don't ever want to see this bastard on my screen ever. 
    except Exception as e:
        print(f"Error reading from conversations.txt: {e}")
        return f"An error occurred: {e}"

    conversation_history.append({"role": "user", "content": user_input})

        # If you want the user_input logged as 'Master', append it as such but change it to 'user' for the API call. If you want to change it from "Master" in conversation you need to change each instance of "Master" in this code to whatever the new title is. Otherwise shit will break. I kind of understand why, but I also kind of don't. OpenAI's functions are a bit... interesting. Hm. 
    #append_to_conversation("Master", user_input)  # Log the new user input as 'Master'
    #conversation_history.append({"role": "user", "content": user_input})  # But add it as 'user' to the API

    # Make the OpenAI API call using the full conversation history
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-1106-preview",
            #Make sure you're using the right model. If you don't have access to GPT-4-1106-preview you're going to get errors. Try it with 3.5 turbo or whatever your account says you're permitted to use. 
            messages=conversation_history
        )
        returned_content = response.choices[0].message.content

        append_to_conversation("Master", user_input, str(message.author.id))
        #append_to_conversation("Vex", returned_content, str(message.author.id))

        #append_to_conversation("Vex", returned_content)  # Log Vex's response with her name
        #return returned_content
    except Exception as e:
        print(f"An error occurred in OpenAI API call: {e}")
        return f"An error occurred: {e}"
    return returned_content


# Run the Discord bot
client.run('#The client code/ID thing on the discord bot implementation goes here. It's one of those keys after making the bot. Kind of hidden. ')
#End of Undo Train. If you still haven't figured out version control and are depending on undo spam to roll back the fact that you fucked your code into instability again then stop undoing here dumbass. Christ. For fucks sake you have an IDE use it. 
