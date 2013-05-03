function next_video() {
    return data[cat]['videos'][++counter];
}

function prev_video() {
    return data[cat]['videos'][--counter];
}

function has_next() {
    if (counter < data[cat]['videos'].length-1)
        return true;
    else {
        load_more();
        return (counter < data[cat]['videos'].length-1) 
    }
}

function has_prev() {
    return (counter > 0);
}

function add_videos(v) {
    data[cat]['videos'].push(v);
}

function load_videos() {
    var compiled = _.template($('#playlist_template').html()),
        video;
    for (i in data[cat]['videos']) {
        video = data[cat]['videos'][i];
        $('.jTscroller').append(compiled({ id: i, vid: video['vid'], title: video['title'] }))
    }
    $(".darken").click(playListClick);

}

function set_title(title, url) {
    $('#title').html(title);
    $('#title').attr({href: "http://www.reddit.com/" + url});
}

function load_more() {
    console.log("Loading more");
    $.ajax({
        method: "GET",
        url: "../" + subreddit, 
        contentType: "application/json", 
        data: {page: ++data[cat]['page'], cat: cat},
        success: function (resp) {
            resp = JSON.parse(resp);
            var compiled = _.template($('#playlist_template').html()),
                video,
                last_id = data[cat]['videos'].length-1;
            //$('.jTscroller').empty();
            for (i in resp['videos']) {
                add_videos(resp['videos'][i]);
                video = resp['videos'][i];
                $('.jTscroller').append(compiled({ id: ++last_id, vid: video['vid'], title: video['title'] }))
            }
            $(".darken").click(playListClick);
        },
        error: function (resp) {
            console.log(resp);
        }
        });
}

function change_cat(e) {
    var newCat = e.options[e.selectedIndex].value;
    if (newCat == cat)
        return false;
    else if (newCat in data) {
         cat = newCat;
        $('.jTscroller').css({left: 0});
        $('.jTscroller').empty();
         load_videos();
    }
    else {
        cat = newCat;
        data[cat] = {}
        data[cat]['videos'] = [];
        data[cat]['page'] = 0;
        $('.jTscroller').css({left: 0});
        $('.jTscroller').empty();
        load_more();
    }
}

// autofocus from iframe if on chrome or safari
function keepFocused() {
    window.focus();
}

function playListClick() {
    counter = parseInt($(this).attr('data-id')-1);
    console.log(counter);
    player.stopVideo();
    var next = next_video();
    player.loadVideoById(next['vid']);
    $('body').css({'background-image': "url('./static/bg/" + next['vid'] + ".png')"})
    set_title(next['title'], next['permalink']);
}

// autoplay video
function onPlayerReady(event) {
    event.target.playVideo();
}

// check for video complete event
function onPlayerStateChange(event) {
    if(event.data === 0) {
        nextVideo();
    }
}

// check for video error
function onPlayerError(event) {
    console.log("Player error, skipping video");
    nextVideo();
}

// load the next video
function nextVideo(){
    var next;
    if (has_next()){
        next = next_video();
        player.stopVideo();
        player.loadVideoById(next['vid']);
        set_title(next['title'], next['permalink']);
        $('body').css({'background-image': "url('./static/bg/" + next['vid'] + ".png')"})
    }
}

// load the previous video
function prevVideo(){
    var next;
    if (has_prev()){
        next = prev_video();
        player.stopVideo();
        player.loadVideoById(next['vid']);
        set_title(next['title'], next['permalink']);
        $('body').css({'background-image': "url('./static/bg/" + next['vid'] + ".png')"})
    }
}

// pause the video
function pauseVideo(){
    console.log('pausing video ' + counter);
    if (pauseFlag < 1){
        player.pauseVideo();
        document.getElementById("pButton").innerHTML="<i class='icon-play'></i>";
        pauseFlag = 1;
    }
    else {
    	player.playVideo();
    	document.getElementById("pButton").innerHTML="<i class='icon-pause'></i>";
    	pauseFlag = 0;
    }
}
