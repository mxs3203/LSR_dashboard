var refCurveFile = null;
var not_done = true

$("#refCurveFile").on('input', function() {
   refCurveFile = this.files[0];
});


$( "#setTemp" ).click(function() {
 var temp = $("#temperature").val();
 $.ajax({
        url: "/set_lsr_temp",
        data: {task:"temp",value:temp},
        async: true,
        type: "GET",
        dataType: "json",
        success: function (data) {
            console.log(data);
        },
        error: function () {
            console.log("Something went wrong");
        },
    });
});


$( "#findCurve" ).click(function() {
        not_done = true
        var formData = new FormData();
        formData.append('file',refCurveFile)

        if(refCurveFile != null){
            setTimeout(function() {
                get_ga_results();
            }, 1000);

            $.ajax({
                url: "/findCurve",
                data: formData,
                async: true,
                type: "POST",
                processData: false,
                contentType: false,
                success: function (data) {
                    console.log(data);
                },
                complete: function(){
                    not_done = false
                },
                error: function () {
                    console.log("Something went wrong");
                },
            });
        } else {
            alert("You cannot start process of finding curve before loading the reference curve!")
        }

});



function get_ga_results(){
    $.ajax({
      url: '/get_current_solution',
      type: 'GET',
      async: true,
      success: function(data){
        data = JSON.stringify(data);
        console.log(data)
        $('input[name=lsr_params]').val(data["solution"])
      }
      complete:function(data){
       if (not_done){
        setTimeout(get_ga_results,5000);
       }

      }
     });
}



$( "#abortLSR" ).click(function() {
 $.ajax({
        url: "/abort_lsr",
        data: {},
        async: true,
        type: "GET",
        dataType: "json",
        success: function (data) {
            console.log(data);
        },
        error: function () {
            console.log("Something went wrong");
        },

    });

});

$(function() {
    "use strict";

     // chart 1
	 
		  var ctx = document.getElementById('chart1').getContext('2d');
		
			var myChart = new Chart(ctx, {
				type: 'line',
				data: {
					labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct"],
					datasets: [{
						label: 'New Visitor',
						data: [3, 3, 8, 5, 7, 4, 6, 4, 6, 3],
						backgroundColor: '#fff',
						borderColor: "transparent",
						pointRadius :"0",
						borderWidth: 3
					}, {
						label: 'Old Visitor',
						data: [7, 5, 14, 7, 12, 6, 10, 6, 11, 5],
						backgroundColor: "rgba(255, 255, 255, 0.25)",
						borderColor: "transparent",
						pointRadius :"0",
						borderWidth: 1
					}]
				},
			options: {
				maintainAspectRatio: false,
				legend: {
				  display: false,
				  labels: {
					fontColor: '#ddd',  
					boxWidth:40
				  }
				},
				tooltips: {
				  displayColors:false
				},	
			  scales: {
				  xAxes: [{
					ticks: {
						beginAtZero:true,
						fontColor: '#ddd'
					},
					gridLines: {
					  display: true ,
					  color: "rgba(221, 221, 221, 0.08)"
					},
				  }],
				   yAxes: [{
					ticks: {
						beginAtZero:true,
						fontColor: '#ddd'
					},
					gridLines: {
					  display: true ,
					  color: "rgba(221, 221, 221, 0.08)"
					},
				  }]
				 }

			 }
			});  
		

		
   });	 

