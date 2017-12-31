var dgram = require('dgram')
var serverSocket = dgram.createSocket('udp4');
message = '{"level":{"angle":"179","speed":"10"},"virt":{"angle":"90","speed":"10"}}'
serverSocket.send(message,0,message.length,9997,"192.168.137.39")
console.log("send a message");