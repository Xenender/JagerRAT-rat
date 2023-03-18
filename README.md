# JagerRAT

<h2>DISCLAIMER:</h2>

JagerRat is a malware created solely for educational purposes. It is intended to be used in a personal and controlled environment only. By downloading and using JagerRat, you agree that you will not use it for malicious purposes or in any illegal activity.

The creator of JagerRat assumes no responsibility for any damages or losses caused by the use of this software. The user is solely responsible for any consequences that may arise from the use of JagerRat.

<h3>What is JagerRAT</h3>

JagerRAT is an R.A.T(remote administration tool) developed in Python. It serves as well as creator of the payload as a server that listens to connections.
The generated payload works on the principle of the reverse TCP, it allows the attacker to take a complete control of the victim's computer.

<h3>How does it work</h3>

As said before, the generated payload operates on the principle of Reverse TCP: when it is opened by a victim, it will initiate a TCP connection to the attacker having launched JagerRAT listener.
At that time the attacker has a complete control to the victim's computer: he has access to a shell and the various features of JagerRAT which will be detailed next.


<h3>Implemented features</h3>

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



<h3>Composition of the project</h3>

     -JagerRAT.py  -> main file (server and listener)
     -directory /app/  -> contient les fichiers necessaire au fonctionnement de JagerRAT.py
     
    
<h3>How to use it</h3>

    -Download main files/directories: JagerRAT.py and /app. all files should be organized like in github.
    -Download the different python libraries needed (See at the end of the README).
    -Run JagerRAT.py using python3.
    -Create a payload using the utility.
    -Launch the listening server on the same parameters.
    -Execute the payload on a victim machine (If the file is not converted into .exe the victim must install the necessary libraries, see end of README).
    -A connection appears on the listening server.
    -The attacker now has access to all implemented features (See: "Implemented features").


<h3>Required python libraries</h3>

for the attacker:

    -see missing libraries at launch
    
    
for the victim:

    -pyautogui
    -pyaudio
    -playsound
    -mutagen
    -pynput
    -opencv-python
    -Pillow
    
    
how to install these libraries:

    -python3 -m pip install 'library'
    

for more flexibility, create an .exe from the generated payload using 'pyinstaller':

    -pip install pyinstaller
    -pyinstaller -F --clean -w payload.py
