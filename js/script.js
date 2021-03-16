var identified_characters = [];

// because top is a reserved word (but not that webstorm bothered to tell me)
var upper = -1;
var left = -1;
var lower = -1;
var right = -1;
var chr = "";

// this are needed when returning values back to the server
var language_model;
var page_id;
var index_wrt_lang_model;

// these are needed to load in the image
// todo - could simplify this a bit
var ship;
var year;
var month;
var page;


var upper_left_corner_x;
var upper_left_corner_y;
var width;
var height;

const source = document.getElementById('character');
// const result = document.getElementById('result');

const inputHandler = function(e) {
    // result.innerHTML = e.target.value;
    var button = document.getElementById("add")
    if ((upper != lower) && (left != right) && (e.target.value.length > 0)) {
        button.disabled = false
    }
    else {
        button.disabled = true
    }
}

source.addEventListener('input', inputHandler);
// source.addEventListener('propertychange', inputHandler);

function setup(){
    // making sure to reset completely
    upper = -1;
    left = -1;
    lower = -1;
    right = -1;
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
    image.src = "images/"+ship+"-"+year+"-"+month+"-"+page+"-aligned.png";

    var submit_button = document.getElementById("submit")
    submit_button.disabled = true

    var add_button = document.getElementById("add")
    add_button.disabled = true

    var reset_button = document.getElementById("reset")
    reset_button.disabled = true

    var paragraph = document.getElementById("identified_characters");
    paragraph.textContent = "Identified Characters:  ";
    paragraph.style.color = 'black';

}


function set_image(data){
    console.log(data)
    language_model = data["language_model"]
    page_id = data["page_id"]
    ship = data["ship_name"]
    year = data["year"]
    month = data["month"]
    page = data["page_number"]
    index_wrt_lang_model = data["index_wrt_lang_model"]

    upper_left_corner_x = data["left"]
    upper_left_corner_y = data["top"]
    width = data["right"] - data["left"]
    height = data["bottom"] - data["top"]
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
            left = parseInt(c.x);
            upper = parseInt(c.y);
            // todo - do we need to switch top and bottom?
            lower = parseInt(c.y2);
            right = parseInt(c.x2);

            var elem = document.getElementById('character');
            var temp_chr = elem.value

            var button = document.getElementById("add")
            if ((upper != lower) && (left != right) && (temp_chr.length > 0)) {
                button.disabled = false
            }


        },
            onRelease: function(c) {
                var button = document.getElementById("add")
                button.disabled = true
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
        body: JSON.stringify({"language_model":language_model,
            "page_id":page_id,
            "index_wrt_lang_model":index_wrt_lang_model,
            "identified_characters":identified_characters})
    }).then(response => getTile())

}

function empty() {
    var add_button = document.getElementById("add")
    var submit_button = document.getElementById("submit")
    var reset_button = document.getElementById("reset")

    if (document.getElementById('isEmpty').checked)
    {
        add_button.disabled = true
        submit_button.disabled = false

        identified_characters = [[null,null,null,null,"empty"]]
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

    if (chr == "empty") {
        // todo - make sure if that you say empty, you don't enter anything else
        identified_characters.push([null,null,null,null,"empty"])

    }
    else if ((upper != lower) && (left != right) && (chr != "")) {
        identified_characters.push([{"top":upper,"left":left,"bottom":lower,"right":right,"character":chr}])

        var canvas = $("#my_canvas")[0];
        var context = canvas.getContext("2d");

        context.fillStyle = 'rgba(0,0,255,0.5)';
        // console.log(left,top,right-top,bottom-top)
        context.fillRect(left,upper,right-left,lower-upper);

        var jcrop_api = $('#my_canvas').data("Jcrop");
        jcrop_api.release()
    }

    // we can't select empty if we have already entered a character
    var empty = document.getElementById('isEmpty')
    empty.disabled = true

    // once we have entered at least one character, we can submit
    var button = document.getElementById("submit")
    button.disabled = false

    // but we cannot add another character until we actually select something
    var button = document.getElementById("add")
    button.disabled = true

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
    var reset_button = document.getElementById("reset")
    reset_button.disabled = false
}

function resetTile(){
    identified_characters = []
    setup()
    var jcrop_api = $('#my_canvas').data("Jcrop");
    jcrop_api.release()

    // we can't select empty if we have already entered a character
    var empty = document.getElementById('isEmpty')
    empty.disabled = false
    empty.checked = false

    var button = document.getElementById("add")
    button.disabled = false
}

window.onload = getTile
