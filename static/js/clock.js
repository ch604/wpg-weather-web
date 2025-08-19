// update the clock once per second
function updateClock() {
	const localTime = new Date();

	const hours = String(localTime.getHours()).padStart(2, '0');
	const minutes = String(localTime.getMinutes()).padStart(2, '0');
	const seconds = String(localTime.getSeconds()).padStart(2, '0');
	const currentTime = `${hours}:${minutes}:${seconds}`;

	document.getElementById('current-time').textContent = currentTime;
}

setInterval(updateClock, 1000);
updateClock();