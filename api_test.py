import pyaudio
import speech_recognition as sr
import requests
import json
from gtts import gTTS
import os
import subprocess
import serial


# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

# Reading Microphone as source
# listening the speech and store in audio_text variable
with sr.Microphone() as source:
    print("Talk")
    audio_text = r.listen(source, phrase_time_limit=5)  # limit phrase to 5 seconds
    print("Time over, thanks")

try:
    # using google speech recognition
    print("Text: "+r.recognize_google(audio_text))
    text = r.recognize_google(audio_text)
except:
     print("Sorry, I did not get that")
     text = ""

# send POST request to GPT-3 API with text as input
url = 'https://api.openai.com/v1/engines/text-davinci-002/completions'  # using 'text-davinci-002' model
headers = {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer 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',
}
data = {
    'prompt': text,
    'max_tokens': 60
}
response = requests.post(url, headers=headers, data=json.dumps(data))
response_json = response.json()

# print out the entire response for debugging
print(response_json)

# check if 'choices' key is in the response
if 'choices' in response_json:
    # get the model's response
    gpt3_response = response_json['choices'][0]['text'].strip()
else:
    print("Error: the response from the OpenAI API did not include a 'choices' key.")
    gpt3_response = ""

# convert the text to speech
tts = gTTS(text=gpt3_response, lang='en')
tts.save("output.mp3")

if "walk" or "move" in text:
    # Open the serial connection
    subprocess.call(["espeak", "Yes, sir. I'm comming to you"])
    ser = serial.Serial('/dev/ttyUSB0', 9600)  # Replace '/dev/ttyUSB0' with the correct serial port and baud rate
    # Send motion orders
    motion_command = 'F'  # Replace 'F' with the desired motion command
    ser.write(motion_command.encode())

    # Close the serial connection
    ser.close()
else:
    # use espeak to output the speech
    subprocess.call(["espeak", gpt3_response])

