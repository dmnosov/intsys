#!/bin/bash
poetry run python server.py &
SERVER_PID=$!

sleep 2

poetry run python client.py 1 &
CLIENT1_PID=$!

poetry run python client.py 2 &
CLIENT2_PID=$!

sleep 300

kill $SERVER_PID $CLIENT1_PID $CLIENT2_PID