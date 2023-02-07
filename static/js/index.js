var refCurveFile = null;
var not_done = true;
var nm = null;
var recon_curve = null;
var ref_curve = null;
var MAX_GEN = 10;
$('.loader').hide();
$('.loaderText').hide();
$('#progressBar').hide();
$('#connected').hide();
$('#disconnected').show();
$('#saveExperiment').prop('disabled', true);
getStatus();

function progress(how_much) {
    var elem = document.getElementById("progressBar");
    var width = 1;
    var id = setInterval(frame, 1);
    function frame() {
      if (width >= how_much) {
        clearInterval(id);
      } else {
        if (width <= 100){
            width++;
            elem.style.width = width + "%";
            elem.innerHTML = width  + "%";
        }
      }
    }

}

function openFigure(element){
    console.log(element.innerHTML)
    location.href = '/figure?figure='+element.innerHTML.split("static/Figures/")[1];
}

function getStatus(){

    $.ajax({
          url: '/get_status',
          type: 'GET',
          async: false,
          success: function(data){
            data = $.parseJSON(JSON.stringify(data));
            console.log(data)
            if(data['connected']){
                $('#connected').show();
                $('#disconnected').hide();
                $('input[name=current_temp]').val(data['temp'] + "℃");
            }
          },
          complete:function(data){
            setTimeout(getStatus,4000);

          }
         });
}



$("#refCurveFile").on('input', function() {
   refCurveFile = this.files[0];
});

$( "#setTemp" ).click(function() {
 var temp = $("#temperature").val();
 $.ajax({
        url: "/set_lsr_temp",
        data: {task:"temp",value:temp},
        async: false,
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
            $(':button').prop('disabled', true);
            $('.loader').show();
            $('.loaderText').show();
            $('#progressBar').show();
            setTimeout(function() {
                get_ga_results();
            }, 3000);

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
                    $('#progressBar').hide();
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
        $('input[name=current_temp]').val(data['temp'] + "℃");
        makeplots();
        progress((data['generation']/MAX_GEN * 100));
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
				  display: true,
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



