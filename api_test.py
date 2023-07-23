import pyaudio
import speech_recognition as sr
import requests
import json
from gtts import gTTS
import os
import subprocess
import serial
import time


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
    'Authorization': 'Bearer OPEN_AI_API_KEY',
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


if "walk" in text or "move" in text:
    # Open the serial connection
    subprocess.call(["espeak", "Yes, sir. I'm comming to you"])
    port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0-port0'
    ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=3)  # Replace '/dev/ttyUSB0' with the correct serial port and baud rate
    # Send motion orders
    motion_command = '#M1'  # Replace 'F' with the desired motion command
    ser.write((motion_command + '\n').encode())
    time.sleep(3)
    # Close the serial connection
    ser.close()



elif "stop" in text:
    # Open the serial connection
    subprocess.call(["espeak", "Yes, sir. I stop"])
    port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0-port0'
    ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=3)  # Replace '/dev/ttyUSB0' with the correct serial port and baud rate
    # Send motion orders
    motion_command = '#M0'  # Replace 'F' with the desired motion command
    ser.write((motion_command + '\n').encode())
    time.sleep(3)
    # Close the serial connection
    ser.close()



elif "wave" in text or "hands" in text:
    # Open the serial connection
    subprocess.call(["espeak", "Yes, sir. I'm waving my hands"])
    port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0-port0'
    ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=3)  # Replace '/dev/ttyUSB0' with the correct serial port and baud rate
    # Send motion orders
    motion_command = '#M5'  # Replace 'F' with the desired motion command
    ser.write((motion_command + '\n').encode())
    time.sleep(3)

    # Close the serial connection
    ser.close()



elif "dance" in text:
    # Open the serial connection
    subprocess.call(["espeak", "Yes, sir. I'm dancing for you"])
    port = '/dev/serial/by-path/platform-3f980000.usb-usb-0:1.3:1.0-port0'
    # Replace '/dev/ttyUSB0' with the correct serial port and baud rate
    # Send motion orders
    motion_commands = ['#M6', '#M8']
    for i in range(20):
        ser = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)
        order = i % 2
        ser.write((motion_commands[order] + '\n').encode())
        time.sleep(1)
    # Close the serial connection
    ser.close()


else:
    # use espeak to output the speech
    subprocess.call(["espeak", gpt3_response])
