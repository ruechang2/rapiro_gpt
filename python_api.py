import openai
import subprocess
import socket
import re
import time
import serial


openai.api_key = "<OpenAI API KEY>"

host = '127.0.0.1'   
port = 10500         
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host, port))
time.sleep(3)
re_word = re.compile('WORD="([^"]+)"')

def jtalk(t):
    open_jtalk=['open_jtalk']
    mech=['-x','/var/lib/mecab/dic/open-jtalk/naist-jdic']
    # htsvoice=['-m','/usr/share/hts-voice/mei/mei_bashful.htsvoice'] # 女性の声が良い方はこのコメントを外す
    htsvoice=['-m','/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice']
    speed=['-r','1.0']
    quolity=['-a','0.5']
    toon=['-fm','0.2']
    yokuyo=['-jf','1.0']
    outwav=['-ow','test.wav']
    cmd=open_jtalk+mech+htsvoice+speed+quolity+toon+yokuyo+outwav
    c = subprocess.Popen(cmd,stdin=subprocess.PIPE)
    c.stdin.write(t.encode('utf-8'))
    c.stdin.close()
    c.wait()
    aplay = ['aplay','-q','test.wav','-Dhw:0,0']
    wr = subprocess.Popen(aplay)

    command = b'TERMINATE\n'
    client.sendall(command)
    wr.wait()  # 音声再生が終了するまで待機
    command = b'RESUME\n'
    client.sendall(command)

def completion(new_message_text:str, settings_text:str = '', past_messages:list = []):
    if len(past_messages) == 0 and len(settings_text) != 0:
        system = {"role": "system", "content": settings_text}
        past_messages.append(system)
    new_message = {"role": "user", "content": new_message_text}
    past_messages.append(new_message)

    result = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=past_messages
    )
    response_message = {"role": "assistant", "content": result.choices[0].message.content}
    past_messages.append(response_message)
    response_message_text = result.choices[0].message.content
    return response_message_text, past_messages

def dialog():
    # 以下のsystem_settingsを変更することでキャラを変更できます
    system_settings = """
    You are a servant taking care of your owner.
    """
    messages = []
    recog_text = ""
    data = ""
    try:
        while recog_text != "Session Ends":
            print("Recognizing")
            while(data.find("</RECOGOUT>\n.") == -1):
                data += str(client.recv(1024).decode('shift_jis'))

            recog_text = "" # 単語を抽出
            for word in filter(bool, re_word.findall(data)):
                recog_text += word

            print("Recognized" + recog_text)
            if recog_text == "Reset":
                messages.clear()
                print("messages:",messages)
                recog_text = ""
                data = ""
                jtalk("System reset")
                continue

            if recog_text in "walk" or "move":
                # Open the serial connection
                jtalk("Yes, sir. I'm comming to you")
                ser = serial.Serial('/dev/ttyUSB0', 9600)  # Replace '/dev/ttyUSB0' with the correct serial port and baud rate
                # Send motion orders
                motion_command = 'F'  # Replace 'F' with the desired motion command
                ser.write(motion_command.encode())

                # Close the serial connection
                ser.close()
                continue



            new_message, messages = completion(recog_text, system_settings, messages)
            print("new_message:",new_message)

            jtalk(new_message)
            data = ""
    except KeyboardInterrupt:
        print('PROCESS END')
        command = b'DIE\n'
        client.send(command)
        client.close()

def main():
    data = ""
    try:
        while True:
            print("Recognizing")
            while(data.find("</RECOGOUT>\n.") == -1):
                data += str(client.recv(1024).decode('shift_jis'))

            recog_text = "" # 単語を抽出
            for word in filter(bool, re_word.findall(data)):
                recog_text += word

            print("Recognized:" + recog_text)
            if recog_text == "Jarvis":
                jtalk("Yes, sir. I'm here for you")
                dialog()

            data = ""
    except KeyboardInterrupt:
        print('PROCESS END')
        command = b'DIE\n'
        client.send(command)
        client.close()


if __name__ == '__main__':
    main()


