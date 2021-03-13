var identified_characters = [];

var x;
var y;
var w;
var h;
var chr;


function setup(){
    var canvas = document.getElementById('my_canvas');
    var ctx = canvas.getContext('2d');
    canvas.width = 300;
    canvas.height = 300;
    var image = new Image();
    image.onload = function() {
        // https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/drawImage
        ctx.drawImage(image, 100,100,40,40,0,0,300,300);
    };
    image.src = "/home/ggdhines/bear/page9-1.png";
}
// let promise = fetch("");
// console.log(promise)

fetch("http://127.0.0.1:5000/login", {
    method: "GET", // "GET/POST"
    headers: {
        "Content-Type": "application/json"
    }
}).then(response => response.json())
    .then(data => console.log(data));

// window.onload = setup;
setup();

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
        allowResize: true
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

    var elem = document.getElementById('character');
}