var identified_characters = [];

var x;
var y;
var w;
var h;
var chr;

var ship;
var year;
var month;
var page;

var upper_left_corner_x;
var upper_left_corner_y;
var width;
var height;

function setup(){
    var canvas = document.getElementById('my_canvas');
    var ctx = canvas.getContext('2d');

    var image = new Image();
    var buffer = 20
    image.onload = function() {
        // https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/drawImage
        ctx.drawImage(image, upper_left_corner_x-buffer,upper_left_corner_y-buffer,width+2*buffer,height+2*buffer,0,0,200,200)
    };
    image.src = "images/"+ship+"-"+year+"-"+month+"-"+page+"-aligned.png";
}


function set_image(data){
    ship = data["ship_name"]
    year = data["year"]
    month = data["month"]
    page = data["page_number"]

    upper_left_corner_x = data["left"]
    upper_left_corner_y = data["top"]
    width = data["right"] - data["left"]
    height = data["bottom"] - data["top"]
    setup()
}

fetch("http://127.0.0.1:5000/getTile", {
    method: "GET", // "GET/POST"
    headers: {
        "Content-Type": "application/json"
    }
}).then(response => response.json())
    .then(data => set_image(data)
    );

$(document).ready(function(){
        $('#my_canvas').Jcrop({
        onSelect: function(c){
            console.log(c);

            x = parseInt(c.x);
            y = parseInt(c.y);
            h = parseInt(c.h);
            w = parseInt(c.w);
        },
        allowSelect: true,
        allowMove: true,
        allowResize: true,
            boxWidth: 700
    })

})

function addCharacter() {

    var elem = document.getElementById('character');
    chr = elem.value
    elem.value = ""

    if ((w > 0) && (chr != "")) {
        identified_characters.push([x,y,w,h,chr])

        var canvas = $("#my_canvas")[0];
        var context = canvas.getContext("2d");

        context.fillStyle = 'rgba(0,0,255,0.5)';
        context.fillRect(x,y,w,h);

        var jcrop_api = $('#my_canvas').data("Jcrop");
        jcrop_api.release()
    }

    var elem = document.getElementById("add");

}

function resetTile(){
    identified_characters = []
    setup()
    var jcrop_api = $('#my_canvas').data("Jcrop");
    jcrop_api.release()

    // var elem = document.getElementById('character');
}