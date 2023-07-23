import serial
import speech_recognition as sr
import requests
import json
from gtts import gTTS
import os
import subprocess
import time

# Initialize recognizer class (for recognizing the speech)
r = sr.Recognizer()

while True:
    # Reading Microphone as the source
    with sr.Microphone() as source:
        print("Talk")
        audio_text = r.listen(source, phrase_time_limit=5)  # Limit phrase to 5 seconds
        print("Time over, thanks")

    try:
        # Using Google Speech Recognition
        recognized_text = r.recognize_google(audio_text)
        print("Text: " + recognized_text)
        text = recognized_text.lower()  # Convert to lowercase for easier comparison

        if "finish" in text:  # Exit the loop and stop the code if "finish" is spoken
            break

        # Send POST request to GPT-3 API with text as input
        url = 'https://api.openai.com/v1/engines/text-davinci-002/completions'
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

        # Convert the text to speech
        tts = gTTS(text=gpt3_response, lang='en')
        tts.save("output.mp3")

        if "walk" in text or "move" in text:
            # Open the serial connection
            subprocess.call(["espeak", "Yes, sir. I'm coming to you"])
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
            # Use espeak to output the speech
            subprocess.call(["espeak", gpt3_response])

    except sr.UnknownValueError:
        print("Sorry, I did not understand.")
    except sr.RequestError as e:
        print("Error: {0}".format(e))
    except Exception as e:
        print("Error: {0}".format(e))
        text = ""
