### Prompt to make server-client echo chat system.
Planning to make server-client echo chat system. There will be two parts.

#### Concepts
1. Server.py
2. Client.py

role of server.py -> open socket and wait. when client is connected and message is received from client, send back to client.

role of client.py -> connect to server socket and send some message.

#### GUI context
implement concepts as GUI using tkinter.
1. add text box and button to send message to server.
2. add connect button and setting fields(HOST and PORT). connect to the server refer to this fields.
3. Server and Client can print timestamps with events.

#### Integration
1. create main.py so that I can execute only one file to test server and client.

#### Summary
1. add comment to socket related code to check sequence of server-client communication.