$(function(){

	player = document.getElementById("player");
	var songIndex = null;
	var isPlaying = false;
	var artistsList = []

	getSongs = function(filter, artist, genre) {
		asyncGetSongs(filter, artist, genre);
	}

	displaySongs = function(songs) {
		// Populate table
		var table;
		table = "<thead><tr><th>Genre</th><th>Artist</th><th>Album</th><th>Title</th><th>Download</th></tr></thead><tbody>";
		$.each(songs["files"], function(index, value) {
			var odd = (index%2 == 0) ? "": " odd";
			table += "<tr class='songItem" + odd + "' attr-index='" + value["index"] + "'><td> " + value['genre'] + "</td><td> " + value['artist'] + "</td><td> " + value['album'] + "</td><td> " + value['title'] + "</td><td><a href='/file/?path=" + value["file"] +"' target='_blank' class='download'><img src='/static/images/download.png' alt='download' /></a></td></tr>";
		});
		table += "</tbody>";
		$("#songList").html(table);
		index =  $(".songItem:first").attr("attr-index");
		$(".songItem:first").addClass("active");
		if (songIndex == null && index != undefined) {
			getSong(index);
		}
	};

	// Actions
	$(".plyr_control ul li a#ppButton").click(function(){
		if ( $(this).hasClass("pplay") ) {
			startSong();
			isPlaying = true;
		} else {
			stopSong();
			isPlaying = false;
		}
	});

	$(document).on("click", ".songItem", function(){
		getSong( $(this).attr("attr-index") );
		songIndex = $(this).attr("attr-index");
		$("tr.active").removeClass("active");
		$(this).addClass("active");
	});
				
	$("#filterGenres").change(function(){
		console.log(artistsList);
		artists = $("#filterArtists");
		artists.find("option").remove();
		artists.append($("<option />").val("").text("-- Artist --"));
		for (var i=0;i<artistsList.length;i++) {
			artist = artistsList[i];
			if ($(this).val() != "") {
				if ($(this).val() == artist[1]) {
					if (!$("#filterArtists option[value='" + artist[0] + "']").is("option")) {
 	                   artists.append($("<option />").val(artist[0]).text(artist[0]));
                    }
				}
			} else {
				if (!$("#filterArtists option[value='" + artist[0] + "']").is("option")) {
                	artists.append($("<option />").val(artist[0]).text(artist[0]));
                }
			}
		}
	});

	$("#filterGenres, #filterArtists").change(function(){
		filter();
	});

	$("#filterBtn").click(function(){
		filter();
	});

	$("#filterField").keypress(function(event){
		var keycode = (event.keyCode ? event.keyCode : event.which);
		if(keycode == '13'){
		  filter();  
		}
	  });

	filter = function(){
		var filter = $("#filterField").val();
		var genre = $("#filterGenres").val();
		var artist = $("#filterArtists").val();
		getSongs(filter, artist, genre);
		loadArtists(filter);
		loadGenres(filter);
	};

	$("#filterClearBtn").click(function(){
		$("#filterField").val("");
		$("#filterGenres").val("Genre");
		$("#filterArtists").val("Artist");
		filter();
	});

	showSong = function(songData) {
		stopSong();
		$("#artist").text(songData["infos"]["artist"]);
		$("#album").text(songData["infos"]["album"]);
		$("#genre").text(songData["infos"]["genre"]);
		$("#title").text(songData["infos"]["title"]);
		if (songData["art"] != "") {
			art = "data:" + songData["mime"] + ";base64," + songData["art"];
		} else {
			art = "/static/images/default.png";
		}
		navigator.mediaSession.metadata = new MediaMetadata({
			title: songData["infos"]["title"],
			artist: songData["infos"]["artist"],
			album: songData["infos"]["album"], 
			artwork: [
			  { src: art },
			]
		  });
		$("#thumbnail").attr("src", art)
		$("#player").attr("src", "/file/?path=" + songData["file"]);
		
		if (isPlaying==isPlaying) {
			startSong();
		}
	};

	stopSong = function(){
		$(".plyr_control ul li a#ppButton").addClass("pplay");
		$(".plyr_control ul li a#ppButton").removeClass("ppause");
		player.pause();
		document.title = "Player";
        navigator.mediaSession.playbackState = 'paused';
	};

	startSong = function(){
		$(".plyr_control ul li a#ppButton").addClass("ppause");
		$(".plyr_control ul li a#ppButton").removeClass("pplay");
		player.play();
		document.title = "Player - " + $("#artist").text() + " : " + $("#title").text();
        navigator.mediaSession.playbackState = 'playing';
	};

	// Ajax
	getSong = function(index) {
		$.ajax({
				dataType: "json",
				type:'POST',
				url:'/getInfos',
				data:"index=" + index,
				success: function(data){
				showSong(data);
			}
		});
	};

	loadGenres = function(filter) {
		$.ajax({
				dataType: "json",
				type:'GET',
				url:'/getGenres?filter=' + filter,
				success: function(data){
					genres = $("#filterGenres").empty();
					genres.append($("<option />").val("").text("-- Genre --"));
					$.each(data, function(index, value) {
						genres.append($("<option />").val(value).text(value));
					});
				}
		});
	};

	loadArtists = function(filter) {
		$.ajax({
				dataType: "json",
				type:'GET',
				url:'/getArtists?filter=' + filter,
				success: function(data){
					artists = $("#filterArtists").empty();
					artists.append($("<option />").val("").text("-- Artist --"));
					$.each(data, function(index, value) {
						artistsList.push(value);
						if (!$("#filterArtists option[value='" + value[0] + "']").is("option")) {
   							artists.append($("<option />").val(value[0]).text(value[0]));
						}
                    });
				}
		});
	};
			
	asyncGetSongs = function(filter, artist, genre) {
		$.ajax({
					dataType: "json",
					type: 'POST',
					url: '/getSongs',
					data: {"filter": filter, "artist": artist, "genre": genre},
					success: function(data) {
					displaySongs(data);
				}
		});
	}
	
	updateProgress = function(){
		position = (player.currentTime * 298) / player.duration;
		$(".pslider_dot").css("left", position);
	};	

	previousSong = function() {
		var prev =  $(".songItem[attr-index="+songIndex+"]").prev(".songItem").attr("attr-index");
		if (prev != undefined) {
			$("tr.active").removeClass("active");
			$(".songItem[attr-index="+songIndex+"]").prev(".songItem").addClass("active");
			songIndex = songIndex - 1;
			getSong(songIndex);
		} else {
			isPlaying = false;
			player.pause();
			player.currentTime = 0;
			$(".plyr_control ul li a#ppButton").addClass("pplay");
			$(".plyr_control ul li a#ppButton").removeClass("ppause");
		}
	};

	nextSong = function(){
		var next =  $(".songItem[attr-index="+songIndex+"]").next(".songItem").attr("attr-index");		
		if (next != undefined) {
			$("tr.active").removeClass("active");
			$(".songItem[attr-index="+songIndex+"]").next(".songItem").addClass("active");
			songIndex = next;
			getSong(songIndex);
		} else {
			player.stop;
			player.currentTime = 0;
			isPlaying = false;
			$(".plyr_control ul li a#ppButton").addClass("pplay");
			$(".plyr_control ul li a#ppButton").removeClass("ppause");
            navigator.mediaSession.playbackState = 'paused';
		}
	};

	$(".pleft").click(function(){
		previousSong();
	});

	$(".pright").click(function(){
		nextSong();
	});

	navigator.mediaSession.setActionHandler('nexttrack', function() {
		// Lógica para cambiar a la siguiente pista
		nextSong();
	});
	
	navigator.mediaSession.setActionHandler('previoustrack', function() {
		// Lógica para cambiar a la pista anterior
		prevSong();
	});
	
	navigator.mediaSession.setActionHandler('play', function() {
		startSong();
		// Actualizar estado de sesión, por ejemplo
		navigator.mediaSession.playbackState = 'playing';
	});
	
	  navigator.mediaSession.setActionHandler('pause', function() {
		stopSong();
		navigator.mediaSession.playbackState = 'paused';
	});	

	$(".pslider").click(function(e){
		player.currentTime = (e.offsetX * player.duration ) / 298;
	});

	$(".psliderVolume").click(function(e){
		var volume =  1 - e.offsetY / 94;
		player.volume = volume

		var top = e.offsetY + 10;
		$(".pslider_dotVolume").css("top", top);
	});

	resizePlaylist = function(){
		var top = 180 + 80 + 30;
		newHeight = $(window).height() - top;
		$("#playlist").css("height", newHeight);
	};

	window.onresize = function(event) {
		resizePlaylist();
	}

	getSongs("", "", "");
	loadGenres("");
	loadArtists("");
	$("#player").on("timeupdate", updateProgress);
	$("#player").on("ended", nextSong);
	resizePlaylist();
});
