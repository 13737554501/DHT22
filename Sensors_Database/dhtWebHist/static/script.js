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
$(document).ready(function() {
	updateCharts();
	setInterval(updatehumChart, 5000); 
	setInterval(updateCharts, 5000); 
    setInterval(updatetempChart, 60000); 
});
