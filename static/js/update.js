// call update endpoint every 30 minutes (1800000us)
function updateData() {
	$.ajax({
		url: '/update',
		type: 'GET',
		success: function(response) {
			$(document).html(response);
		}
	})
}

$(document).ready(setInterval(updateData, 1800000))