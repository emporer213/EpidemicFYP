var ButtonModule = function(){
    var button = $("<div><button onClick=\"SaveData()\">Save</button></div>");
    button.appendTo("body");
}

var SaveData = function() {
    send({"type": "save_data"})
}
