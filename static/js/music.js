// play mp3s from the static/audio folder in a constant shuffle loop
const audioPlayer = document.getElementById('music-player');
let currentIndex = 0;
let hasStarted = false;

function playNextTrack() {
    if (mp3Files.length > 0) {
        // get url for the next track
        const nextTrack = `/static/audio/${mp3Files[currentIndex]}`;
        audioPlayer.src = nextTrack;
        var playPromise = audioPlayer.play();

		if (playPromise !== undefined) {
			playPromise.then(_ => {
                // move to the next track in the list after playback starts
                currentIndex++;
			})
			.catch(error => {
				// playback was prevented
            	console.log("Playback was prevented:", error);
			});
		}

        // loop back to the beginning if we reach the end
        if (currentIndex >= mp3Files.length) {
            currentIndex = 0;
        }
    } else {
        console.log("No MP3 files found to play.");
    }
}

// click on the clock to start music, page interaction is required in modern browsers
document.getElementById('current-time').addEventListener('click', () => {
    if (!hasStarted) {
		playNextTrack();
		hasStarted = true;
	}
});

// in the case that autoplay is enabled with a browser switch for headless launch, attempt to play the track on pageload
window.onload = playNextTrack;

// listen for the 'ended' event to play the next track
audioPlayer.addEventListener('ended', playNextTrack);
