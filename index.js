'use strict'
const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http)

let STATE = null; // the current state of the game

// when someone connected, send out the current state
io.on('connection', (socket) => {
  console.log('A connection ' + socket.id + ' established.');
  // send the latest state to the new connector
  io.emit('STATE', { board_size : 40 });
  socket.on('disconnect', () => {
    console.log('Connection ' + socket.id + ' closed.');
  });
});

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

app.post('/', (req, res, body) => {

});

http.listen(3000, () => {
  console.log('listening on port 3000')
});