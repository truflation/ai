The Truflation AI server is located on nft.truflation.com:8080

The web interface runs on that machine and the calls an ssh tunnel
which connects to a GPU server hosted on vast.ai.  The GPU server runs
the AI engine.

The AI engine runs on vast.ai under user joseph.wang@truflation.com

The script vastai.connect.sh creates a tunnel that connects to the AI
server.

To connect with github use
/github connect (token)

