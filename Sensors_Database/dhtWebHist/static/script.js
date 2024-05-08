function updatetempChart() {
    $.ajax({
        url: '/plot/temp', 
        type: 'GET',
        xhrFields: {
            responseType: 'blob' 
        },
        success: function(response) {
            
            var blob = new Blob([response], {type: 'image/png'});
            var url = URL.createObjectURL(blob);
            $('#temppp').attr('src', url); 
        },
        error: function(error) {
            console.error('yy', error);
        }
    });
}
function updatehumChart() {
    $.ajax({
        url: '/plot/hum', 
        type: 'GET',
        xhrFields: {
            responseType: 'blob' 
        },
        success: function(response) {
            
            var blob = new Blob([response], {type: 'image/png'});
           
            var url = URL.createObjectURL(blob);
            $('#humpp').attr('src', url); 
        },
        error: function(error) {
            console.error('yy', error);
        }
    });
}

    function updateCharts() {
        $.getJSON('/plot/data', function(data) {
            
           g1.refresh(data.temp);
           g2.refresh(data.hum);
           $('#last-time').text(data.time);
           $('#Frequ').text(data.freq);
           
        });
    }
// Function to handle the submission of the time input form
function handleTimeFormSubmission() {
    $('#timeForm').submit(function(event) {
        event.preventDefault();
        var exactTime = $('#exact-time').val(); // Get the time from the input

        $.ajax({
            url: '/get_data_by_minute',
            type: 'POST',
            data: { exact_time: exactTime },
            success: function(response) {
                // If the response contains an error message, display it
                if (response.error) {
                    $('#query-result').html('<span style="color: red;">' + response.error + '</span>');
                } else {
                    // Display the retrieved data on the page
                    $('#query-time').text(response.time);
                    $('#query-temp').text(response.temp);
                    $('#query-hum').text(response.humidity);
                }
            },

        });
    });
}



$(document).ready(function() {
	updateCharts();
	setInterval(updatehumChart, 60000); 
	setInterval(updateCharts, 60000); 
    setInterval(updatetempChart, 60000); 
    handleTimeFormSubmission();
});

