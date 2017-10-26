'use strict'
const app = require('express')();
const http = require('http').Server(app);
const io = require('socket.io')(http)

let STATE = ""

app.get('/', (req, res) => {
  res.sendFile(__dirname + '/index.html');
});

io.on('connection', (socket) => {
  console.log('A connection ' + socket.id + ' established.');
  io.emit('STATE', { data : [1, 2, 3, 4, 5, 6] });
  socket.on('disconnect', () => {
    console.log('Connection ' + socket.id + ' closed.');
  });
});

http.listen(3000, () => {
  console.log('listening on port 3000')
});