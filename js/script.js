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

const initial_buffer = 10
var current_buffer = initial_buffer

const empty_button = document.getElementById('isEmpty')
const add_button = document.getElementById("add")
const submit_button = document.getElementById("submit")
const reset_button = document.getElementById("reset")
const zoomin_button = document.getElementById("zoomin")
const reset_zoom = document.getElementById("resetzoom")

const source = document.getElementById('character');

const display_tile_size = 250;

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


var image = new Image();

function setup(){
    // making sure to reset completely
    x_min = -1;
    x_max = -1;
    y_min = -1;
    y_max = -1;
    chr = "";

    current_buffer = initial_buffer

    var canvas = document.getElementById('my_canvas');
    var ctx = canvas.getContext('2d');
    identified_characters = []

    image.onload = draw;
    image.src = "images/"+file_prefix+"-aligned.png";

    // reset the buttons
    submit_button.disabled = true
    add_button.disabled = true
    reset_button.disabled = true
    empty_button.checked = false
    empty_button.disabled = false
    zoomin_button.disabled = true
    reset_zoom.disabled = true

    var paragraph = document.getElementById("identified_characters");
    paragraph.textContent = "Identified Characters:  ";
    paragraph.style.color = 'black';

}

/**
 * draw displays the tile at the desired current zoom (based on the buffer) as well as any currently selected
 * characters
 */
function draw() {
    var canvas = document.getElementById('my_canvas');
    var ctx = canvas.getContext('2d');

    // not sure if this is necessary but seems safe
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.drawImage(image,
        upper_left_corner_x-current_buffer,
        upper_left_corner_y-current_buffer,
        width+2*current_buffer,
        height+2*current_buffer,
        0,
        0,
        display_tile_size,
        display_tile_size)

    ctx.fillStyle = 'rgba(0,0,255,0.5)';
    let i;
    for (i = 0; i < identified_characters.length; i++) {
        // don't draw rectangles for empty tiles
        if (identified_characters[i]["character"] != null) {
            let character = scale_to_current_display(identified_characters[i])
            ctx.fillRect(character["x_min"],character["y_min"],character["x_max"]-character["x_min"],character["y_max"]-character["y_min"]);
        }
    }

    let boundary = {"x_min":upper_left_corner_x,"y_min":upper_left_corner_y,"x_max":upper_left_corner_x+width,"y_max":upper_left_corner_y+height}
    let scaled_boundary = scale_to_current_display(boundary)

    // draw a boundary where the actual tile corresponds to
    ctx.lineWidth = "2";
    ctx.strokeStyle = "green";
    ctx.beginPath();
    ctx.rect(scaled_boundary["x_min"],scaled_boundary["y_min"],scaled_boundary["x_max"]-scaled_boundary["x_min"],scaled_boundary["y_max"]-scaled_boundary["y_min"]);
    ctx.stroke();
}

function zoomOut() {
    // increase the buffer by 10 pixels (both X and Y axis)
    current_buffer += 10

    draw()

    // we can reset to go back to the original zoom
    // reset_button.disabled = false
    zoomin_button.disabled = false
    reset_zoom.disabled = false

    const jcrop_api = $('#my_canvas').data("Jcrop");
    jcrop_api.release()
}

function zoomIn() {
    current_buffer -= 10
    draw()

    if (current_buffer === initial_buffer) {
        zoomin_button.disabled = true
        reset_zoom.disabled = true
    }

    const jcrop_api = $('#my_canvas').data("Jcrop");
    jcrop_api.release()
}

function resetZoom() {
    current_buffer = initial_buffer
    draw()

    zoomin_button.disabled = true

    const jcrop_api = $('#my_canvas').data("Jcrop");
    jcrop_api.release()
}

function set_image(data){
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

/*
    Does the selected region overlap at least a bit with the tile?
 */
function valid_region_selected() {
    let boundary = {"x_min":upper_left_corner_x,"y_min":upper_left_corner_y,"x_max":upper_left_corner_x+width,"y_max":upper_left_corner_y+height}
    let scaled_boundary = scale_to_current_display(boundary)

    if ((x_max <= scaled_boundary["x_min"]) || (x_min >= scaled_boundary["x_max"]) || (y_max <= scaled_boundary["y_min"]) || (y_min >= scaled_boundary["y_max"])) {
        return false
    }
    else if ((x_min !== x_max) && (y_min !== y_max)) {
        return true
    }
    else {
        return false
    }


}

$(document).ready(function(){
        $('#my_canvas').Jcrop({
        onSelect: function(c){
            x_min = parseInt(c.x);
            y_min = parseInt(c.y);
            y_max = parseInt(c.y2);
            x_max = parseInt(c.x2);

            var elem = document.getElementById('character');
            var temp_chr = elem.value

            if (valid_region_selected() && (temp_chr.length > 0)) {
                add_button.disabled = false
            }
            // else prevents someone from selecting a valid region, enabling the add_button and switching to an invalid region
            else {
                add_button.disabled = true
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


function submitTile(){
    // only do the rescaling just before submit, this will help when we need to redraw any regions as we zoom

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
    }).then(_ => getTile())

}

function scale_to_current_display(character){
    let local_scale = {}

    local_scale["x_min"] = Math.round((character["x_min"] - (upper_left_corner_x - current_buffer))/(width+2*current_buffer) * display_tile_size)
    local_scale["x_max"] = Math.round((character["x_max"] - (upper_left_corner_x - current_buffer))/(width+2*current_buffer) * display_tile_size)

    local_scale["y_min"] = Math.round((character["y_min"] - (upper_left_corner_y - current_buffer))/(height+2*current_buffer) * display_tile_size)
    local_scale["y_max"] = Math.round( (character["y_max"] - (upper_left_corner_y - current_buffer))/(height+2*current_buffer) * display_tile_size)

    return local_scale
}



function scale_to_whole_page(character,buffer_size) {
    // by specifying the buffer size, we can use the original buffer size and not accidentally say the whole
    // image is empty

    let scaled = {"character":character["character"]}
    // rescale points - originally wrt the scale of the displayed tile
    // back to the scale of the source page, i.e. what the rest of the system will understand
    // not hard math, but helpful to have everything all in one place

    // x_min/display_tile_size is how far across the displayed image x_min is as a percentage
    // +2*buffer_size since we are showing slightly more than the selected tile
    scaled["x_min"] = Math.round(character["x_min"]/display_tile_size * (width+2*buffer_size) + upper_left_corner_x - buffer_size)
    scaled["x_max"] = Math.round(character["x_max"]/display_tile_size * (width+2*buffer_size) + upper_left_corner_x - buffer_size)

    scaled["y_min"] = Math.round(character["y_min"]/display_tile_size * (height+2*buffer_size) + upper_left_corner_y - buffer_size)
    scaled["y_max"] = Math.round(character["y_max"]/display_tile_size * (height+2*buffer_size) + upper_left_corner_y - buffer_size)

    return scaled
}

function empty() {
    if (document.getElementById('isEmpty').checked)
    {
        add_button.disabled = true
        submit_button.disabled = false

        let empty_character = {"x_min":0,"y_min":0,"x_max":display_tile_size,"y_max":display_tile_size,"character":null}
        // by using the initial buffer size and the current one, we avoid people accidentally zooming out and saying that
        // the whole page is empty
        // todo - seems reasonable, but might want to double check logic
        let scaled_empty_character = scale_to_whole_page(empty_character,initial_buffer)

        identified_characters = [scaled_empty_character]
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

    const jcrop_api = $('#my_canvas').data("Jcrop");
    jcrop_api.release()

}

function addCharacter() {


    var elem = document.getElementById('character');
    chr = elem.value
    elem.value = ""

    // special case holder for any tiles we might need to skip for whatever reasons
    if (chr === "skip") {
        identified_characters.push([null,null,null,null,"skip"])

    }
    else if (valid_region_selected() && (chr !== "")) {
        let character = {"x_min":x_min,"y_min":y_min,"x_max":x_max,"y_max":y_max,"character":chr}
        let scaled_character = scale_to_whole_page(character,current_buffer)
        identified_characters.push(scaled_character)

        var canvas = $("#my_canvas")[0];
        var context = canvas.getContext("2d");

        context.fillStyle = 'rgba(0,0,255,0.5)';
        context.fillRect(x_min,y_min,x_max-x_min,y_max-y_min);

        const jcrop_api = $('#my_canvas').data("Jcrop");
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

    // go back to the original zoom
    current_buffer = initial_buffer
    setup()

    const jcrop_api = $('#my_canvas').data("Jcrop");
    jcrop_api.release()

    empty_button.disabled = false
    empty_button.checked = false
    add_button.disabled = true
    reset_button.disabled = true
    submit_button.disabled = true
}

window.onload = getTile
