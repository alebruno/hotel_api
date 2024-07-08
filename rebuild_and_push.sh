#!/bin/bash
sudo docker build -t navigar89/rasa:extended -f dockerfile-chatbot .
sudo docker build -t navigar89/hotelrasa:defaultchatbot -f dockerfile-chatbot-readonly .
sudo docker push  navigar89/hotelrasa:defaultchatbot
