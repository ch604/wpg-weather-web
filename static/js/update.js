// socket listener for updates from server
//TODO check for last slide after timer elapses before rendering new slides?
$(document).ready(function(){
    //connect to the socket server.
    const socket = io.connect('http://' + location.hostname + ':' + location.port);

    //receive updates from server
    socket.on('update_slides', function(data) {
        console.log("Received weather updates");
        document.getElementById("slides").innerHTML = data.html;
    });

	socket.on('update_ticker', function(data) {
		console.log("Received news updates");
		document.getElementById("ticker").innerHTML = data.news;
	});

});