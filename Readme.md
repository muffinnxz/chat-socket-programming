Basic Chat App
==============

This is a basic chat application built with Python using socket programming. It allows multiple clients to connect to a server to send and receive messages in real-time.

Features
--------

*   **Real-time Messaging**: Send and receive messages instantly.
*   **Multiple Clients**: Support for multiple clients connected simultaneously.
*   **Private Messaging**: Use the `/whisper` command to send private messages to specific users.
*   **Dynamic Entry/Exit Updates**: Automatically updates all clients when a user enters or leaves the chat.
*   **Group Management**: Users can create, join, and leave groups.
*   **Direct Commands**: Includes commands like `/help` to guide users on command usage.

Prerequisites
-------------

*   Python 3.6 or higher

How to Set Up and Run
---------------------

### Server Setup

1.  Clone the repository:
    
    bashCopy code
    
    `git clone <repository-url>`
    
2.  Navigate to the project directory:
    
    bashCopy code
    
    `cd path/to/project`
    
3.  Start the server:
    
    Copy code
    
    `python server.py`
    

### Client Setup

1.  Open a new terminal window for each client.
2.  Run the client script:
    
    Copy code
    
    `python client.py`
    
    Repeat this step for each client you wish to connect.

How to Use
----------

### General Commands

*   **Send a message**: Simply type your message and press `Enter` to send to the chatroom.
*   **Private message**: Type `/whisper <username> <message>` to send a private message to `<username>`.

### Group Commands

*   **Create a group**: `/group create <groupname>` to create a new group.
*   **Join a group**: `/group join <groupname>` to join an existing group.
*   **Leave a group**: `/group leave` to leave the current group.
*   **List groups**: `/group list` to see a list of available groups.
*   **Group members**: `/group member` to list members of the current group or `/group member <groupname>` to list members of a specific group.

### Special Commands

*   **Ask ChatGPT**: Use `/chatgpt <question>` to ask a question and get a response from ChatGPT.
*   **Help**: Type `/help` to display all available commands and their descriptions.