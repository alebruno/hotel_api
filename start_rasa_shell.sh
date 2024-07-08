#!/bin/bash
# See https://rasa.com/docs/rasa/docker/building-in-docker/
docker run --network host -it -v /home/ale/dev/chatbot/app:/app rasa/rasa:3.6.18-full shell
