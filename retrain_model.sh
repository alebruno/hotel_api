#!/bin/bash
sudo docker run -v /home/ale/dev/chatbot/app:/app navigar89/rasa:extended train --domain domain.yml --data data --out models
