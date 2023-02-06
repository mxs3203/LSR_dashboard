var refCurveFile = null;
var not_done = true;
var nm = null;
var recon_curve = null;
var ref_curve = null;
$('.loader').hide();
$('.loaderText').hide();

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
        $(':button').prop('disabled', true);
        not_done = true
        var formData = new FormData();
        formData.append('file',refCurveFile)
        $('.loader').show();
        $('.loaderText').show();
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

                },
                complete: function(){
                    not_done = false
                    $('.loader').hide();
                    $('.loaderText').hide();
                    $(':button').prop('disabled', false);
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
      async: false,
      success: function(data){
        data = $.parseJSON(JSON.stringify(data));
        $('input[name=lsr_params]').val(data["solution"]);
        ref_curve = data['ref_curve'];
        recon_curve = data['reconstruced_curve'];
        nm = data['nm'];
        $('#fitness_val').text(data['fitness'].toFixed(4));
        $('#generation_val').text(data['generation']);
        $('input[name=current_temp]').val(data['temp']);
        makeplots();
      },
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

function makeplots() {
    "use strict";
		  var ctx = document.getElementById('chart1').getContext('2d');
			var myChart = new Chart(ctx, {
				type: 'line',
				data: {
					labels: nm,
					datasets: [{
						label: 'Reconstructed',
						data: recon_curve,
						backgroundColor: "transparent",
						borderColor: "rgba(255, 10, 10, 0.55)",
						pointRadius :"0",
						borderWidth: 3
					}, {
						label: 'Reference Curve',
						data: ref_curve,
						backgroundColor: "rgba(10, 80, 180, 0.55)",
						borderColor: "rgba(0, 0, 0, 0.55)",
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
					  color: "rgba(221, 221, 221, 0.01)"
					},
				  }],
				   yAxes: [{
					ticks: {
						beginAtZero:true,
						fontColor: '#ddd'
					},
					gridLines: {
					  display: true ,
					  color: "rgba(221, 221, 221, 0.01)"
					},
				  }]
				 }

			 }
			});
}

