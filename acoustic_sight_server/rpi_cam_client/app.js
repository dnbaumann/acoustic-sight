const EventEmitter = require('events');

const express = require('express');
const io = require('socket.io-client');


module.exports = exports = main;


const idleTimeout = 5000;


class App extends EventEmitter {
  constructor(origin, namespace, port, debug) {
    super();

    this.origin = origin;
    this.path = `${this.origin}${namespace}`;
    this.port = port;
    this.debug = debug || false;

    this.lastIamgeUrl = null;

    this.handleImage = this.handleImage.bind(this);

    this.socket = io(this.path);
    this.setupEvents();

    this.server = express();
    this.setupRoutes();
    this.httpServer = null;

    this.shutdownTimeout = null
  }

  stopIfIdle() {
    if (this.shutdownTimeout) {
      clearTimeout(this.shutdownTimeout);
      this.shutdownTimeout = null;
    }

    this.shutdownTimeout = setTimeout(() => {
      console.log(`[RPi Camera client] - Stopping after ${idleTimeout}s timeout...`);
      this.httpServer.close();
      this.socket.close();
      console.log(`[RPi Camera client] - Bye.`);
    }, idleTimeout)
  }

  setupEvents() {
    this.socket.on('connect', function() {
      console.log(`[RPi Camera client] - Connected to ${this.origin}/.`);
    }.bind(this));

    this.socket.on('disconnect', function() {
      console.log(`[RPi Camera client] - Disconnected from ${this.origin}/.`);
    }.bind(this));

    this.socket.on('preview', this.handleImage);
  }

  start() {
    this.httpServer = this.server.listen(this.port, function () {
      console.log(`[RPi Camera client] - Listening on port ${this.port}!`);
      this.stopIfIdle()
    }.bind(this));
  }

  setupRoutes() {
    this.server.get('/', function (req, res) {
      res.setHeader('Content-Type', 'application/json');
      res.send({src: this.lastIamgeUrl});
      this.stopIfIdle();
    }.bind(this));
  }

  handleImage(data) {
    this.lastIamgeUrl = this.origin + data.src;
    if (this.debug) {
      console.log('[RPi Camera client] - Last image:', this.lastIamgeUrl);
    }
  }
}


function main() {
  const origin = process.argv[2] || 'http://127.0.0.1:8000';
  const namespace = process.argv[3] || '/cam';
  const port = Number(process.argv[4] || 3001);
  const debug = Boolean(process.argv[5] || false);

  console.log('[RPi Camera client] - Starting RPi Camera client for:', origin, namespace, port);
  const app = new App(origin, namespace, port, debug);
  app.start();
}

main();
