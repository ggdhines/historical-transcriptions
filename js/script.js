var identified_characters = [];

// as opposed to top/bottom/left/right because of a bunch of name conflicts in html/sql/etc.
var x_min = -1;
var x_max = -1;
var y_min = -1;
var y_max = -1;
var chr = "";

// this are needed when returning values back to the server
var tesseract_model;
var cvae_model;
var local_tile_index;

// these are needed to load in the image
var file_prefix;

// these are used for displaying the right part of the image
var upper_left_corner_x;
var upper_left_corner_y;
var width;
var height;


const empty_button = document.getElementById('isEmpty')
const add_button = document.getElementById("add")
const submit_button = document.getElementById("submit")
const reset_button = document.getElementById("reset")

const source = document.getElementById('character');

const inputHandler = function(e) {
    // result.innerHTML = e.target.value;
    if ((x_min != x_max) && (y_min != y_max) && (e.target.value.length > 0)) {
        add_button.disabled = false
    }
    else {
        add_button.disabled = true
    }
}

source.addEventListener('input', inputHandler);
// source.addEventListener('propertychange', inputHandler);

function setup(){
    // making sure to reset completely
    x_min = -1;
    x_max = -1;
    y_min = -1;
    y_max = -1;
    chr = "";

    var canvas = document.getElementById('my_canvas');
    var ctx = canvas.getContext('2d');
    identified_characters = []

    var image = new Image();
    var buffer = 20
    image.onload = function() {
        // https://developer.mozilla.org/en-US/docs/Web/API/CanvasRenderingContext2D/drawImage
        ctx.drawImage(image, upper_left_corner_x-buffer,upper_left_corner_y-buffer,width+2*buffer,height+2*buffer,0,0,200,200)
    };
    image.src = "images/"+file_prefix+"-aligned.png";

    // reset the buttons
    submit_button.disabled = true
    add_button.disabled = true
    reset_button.disabled = true
    empty_button.checked = false

    var paragraph = document.getElementById("identified_characters");
    paragraph.textContent = "Identified Characters:  ";
    paragraph.style.color = 'black';

}


function set_image(data){
    console.log(data)
    file_prefix = data["file_prefix"]

    tesseract_model = data["tesseract_model"]
    cvae_model = data["cvae_model"]
    local_tile_index = data["local_tile_index"]

    // remember that (0,0) is the top left hand corner
    // so y increases as you go down :/
    upper_left_corner_x = data["x_min"]
    upper_left_corner_y = data["y_min"]
    width = data["x_max"] - data["x_min"]
    height = data["y_max"] - data["y_min"]
    setup()
}

function getTile() {
    fetch("http://127.0.0.1:5000/getTile", {
        method: "GET", // "GET/POST"
        headers: {
            "Content-Type": "application/json"
        }
    }).then(response => response.json())
        .then(data => set_image(data)
        );
}

$(document).ready(function(){
        $('#my_canvas').Jcrop({
        onSelect: function(c){
            console.log(c);

            // todo - rescale!!!
            x_min = parseInt(c.x);
            y_min = parseInt(c.y);
            y_max = parseInt(c.y2);
            x_max = parseInt(c.x2);

            var elem = document.getElementById('character');
            var temp_chr = elem.value

            if ((x_min != x_max) && (y_min != y_max) && (temp_chr.length > 0)) {
                add_button.disabled = false
            }

        },
            onRelease: function(c) {
                add_button.disabled = true
            },
        allowSelect: true,
        allowMove: true,
        allowResize: true,
            boxWidth: 700
    })

})


function submitTile() {
    fetch("http://127.0.0.1:5000/submitTile", {
        method: "POST", // "GET/POST"
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({"file_prefix":file_prefix,
            "tesseract_model":tesseract_model,
            "cvae_model":cvae_model,
            "local_tile_index":local_tile_index,
            "identified_characters":identified_characters})
    }).then(response => getTile())

}

function empty() {
    if (document.getElementById('isEmpty').checked)
    {
        add_button.disabled = true
        submit_button.disabled = false

        identified_characters = [{"x_min":null,"x_max":null,"y_min":null,"y_max":null,"character":null}]
        reset_button.disabled = false
    } else {
        add_button.disabled = false
        submit_button.disabled = true

        // start over again
        identified_characters = []
        reset_button.disabled = true
    }

    // if we have started to enter a character and then decided the tile is empty,
    // remove the character just to emphasize the point
    var elem = document.getElementById('character');
    elem.value = ""
    var jcrop_api = $('#my_canvas').data("Jcrop");
    jcrop_api.release()

}

function addCharacter() {


    var elem = document.getElementById('character');
    chr = elem.value
    elem.value = ""

    // special case holder for any tiles we might need to skip for whatever reasons
    if (chr == "skip") {
        identified_characters.push([null,null,null,null,"skip"])

    }
    else if ((x_min != x_max) && (y_min != y_max) && (chr != "")) {
        identified_characters.push([{"x_min":x_min,"x_max":x_max,"y_min":y_min,"y_max":y_max,"character":chr}])

        var canvas = $("#my_canvas")[0];
        var context = canvas.getContext("2d");

        context.fillStyle = 'rgba(0,0,255,0.5)';
        // console.log(left,top,right-top,bottom-top)
        context.fillRect(left,upper,right-left,lower-upper);

        var jcrop_api = $('#my_canvas').data("Jcrop");
        jcrop_api.release()
    }

    // we can't select empty if we have already entered a character
    empty_button.disabled = true

    // once we have entered at least one character, we can submit
    submit_button.disabled = false

    // but we cannot add another character until we actually select something
    add_button.disabled = true

    var paragraph = document.getElementById("identified_characters");
    // make things look pretty if we have already selected some characters
    if (identified_characters.length > 1) {
        paragraph.textContent += ",";
    }

    // technically we can multiple characters at once, but these should be the exception
    if (chr.length > 1) {
        paragraph.style.color = 'red';
    }
    paragraph.textContent += chr;

    // now that we have entered a character, we can reset if we want to
    reset_button.disabled = false
}

function resetTile(){
    identified_characters = []
    setup()
    var jcrop_api = $('#my_canvas').data("Jcrop");
    jcrop_api.release()


    empty_button.disabled = false
    empty_button.checked = false
    add_button.disabled = true
    reset_button.disabled = true
    submit_button.disabled = true
}

window.onload = getTile
