flask-server
============

## Compile:
```
sudo apt-get install python-pip
sudo pip install virtualenv
sudo pip install Flask
```
## Execute:
```
python hello.py
```
## Usage:

Go to http://localhost:5000 or http://localhost:5000/index

Click the "Smart Register" button, the nfc reader will start scanning tags.
Swipe the NFC phone, and you can see the UUID and public key in the console.
Then click the "Smart Login" button, swipe the phone again and the UUID and signed-nonce will also be shown.

