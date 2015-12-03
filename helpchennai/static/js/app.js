
// GLOBAL VARIABLES
var map;
var chennai = new google.maps.LatLng(13.0827, 80.2707);
var geocoder;
var userLocationMarker;
var userLocation;
var allowedBounds = new google.maps.LatLngBounds(new google.maps.LatLng(
		8, 77), new google.maps.LatLng(
		14, 80.5));
var infoBubble;
var openBubbleEvent;
var dataListenEvent;
if ('addEventListener' in document) {
    document.addEventListener('DOMContentLoaded', function() {
        FastClick.attach(document.body);
    }, false);
}
function getBB() {
	var bBoxNE = map.getBounds().getNorthEast();
	var bBoxSW = map.getBounds().getSouthWest();
	var ne = [ bBoxNE.lng(), bBoxNE.lat() ];
	var nw = [ bBoxSW.lng(), bBoxNE.lat() ];
	var sw = [ bBoxSW.lng(), bBoxSW.lat() ];
	var se = [ bBoxNE.lng(), bBoxSW.lat() ];
	var ne = [ bBoxNE.lng(), bBoxNE.lat() ];
	var bBoxArray = [ ne, nw, sw, se, ne ];
	console.log(bBoxArray);
	return bBoxArray;
}

function uploadRequest(e) {
	if (!e) var e = window.event;
		e.cancelBubble = true;
    if (e.stopPropagation)
		e.stopPropagation();
	// ajax to upload file
	$('#lat').val(marker.getPosition().lat());
	$('#lng').val(marker.getPosition().lng());

	if ($( "#request" ).val() === "Select")
	{
		alert("Please choose request type.");
		return;
	}
	var form_data = new FormData($('#upload-request')[0]);
	console.log(form_data);
	console.log($("#upload-request"));
	$.ajax({
		type : 'POST',
		url : '/uploadrequest',
		data : form_data,
		contentType : false,
		dataType : 'html',
		cache : false,
		processData : false,
		success : function(msg) {
					if (msg == 1){
						alert("Your request is uploaded successfully, Please browse through available help in the map. Stay Safe!");
						if (typeof infoBubble !== "undefined")
							infoBubble.close();
						marker.setVisible(false);
						google.maps.event.trigger(map, 'bounds_changed');
						}
					else
					{
						infoBubbleHelp(msg,marker);
						return false;
					}
						}
		});
	};
function uploadOffer() {
	if (!e) var e = window.event;
		e.cancelBubble = true;
    if (e.stopPropagation)
		e.stopPropagation();
	// ajax to upload file
	$('#lat').val(marker.getPosition().lat());
	$('#lng').val(marker.getPosition().lng());

	if ($( "#offer" ).val() === "Select")
	{
		alert("Please choose offer type.");
		return;
	}

	var form_data = new FormData($('#upload-offer')[0]);
	console.log(form_data);
	console.log($("#upload-offer"));
	$.ajax({
		type : 'POST',
		url : '/uploadoffer',
		data : form_data,
		contentType : false,
		dataType : 'html',
		cache : false,
		processData : false,
		success : function(msg) {
					if (msg == 1)
					{
						alert("Your Offer is uploaded successfully, Please browse through people needing help in the map. Stay Safe!");
						if (typeof infoBubble !== "undefined")
						{
							infoBubble.close();
						}
						marker.setVisible(false);
						google.maps.event.trigger(map, 'bounds_changed');
					}
					else
						infoBubbleHelp(msg,marker);
						}
		});
	};
function getIcon(user) {
	if (user == 'user') {
		return new google.maps.MarkerImage("static/img/markers/user-location.svg",
				null, null, null, new google.maps.Size(64, 64));
	}
}

var marker;
function initialize() {
	var mapOptions = {
		zoom : 18,
		minZoom : 11,
		maxZoom : 18,
		center : chennai,
		disableDefaultUI : true,
        zoomControl: true,
        zoomControlOptions: {
            style: google.maps.ZoomControlStyle.SMALL,
            position: google.maps.ControlPosition.RIGHT_BOTTOM
        },
		styles : [ { "featureType": "poi.government", "stylers": [ { "visibility": "off" } ] },{ "featureType": "road.highway", "elementType": "labels.icon", "stylers": [ { "visibility": "off" } ] },{ "featureType": "road.arterial", "elementType": "labels.icon", "stylers": [ { "visibility": "off" } ] },{ "featureType": "poi.business", "elementType": "labels.icon", "stylers": [ { "visibility": "off" } ] },{ "featureType": "transit", "stylers": [ { "visibility": "off" } ] },{ "featureType": "poi.school", "stylers": [ { "visibility": "off" } ] },{ "featureType": "poi.sports_complex", "stylers": [ { "visibility": "off" } ] },{ "featureType": "poi.attraction", "stylers": [ { "visibility": "off" } ] },{ } ],

	};
	map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);

	marker = new google.maps.Marker({
		map : map,
		anchorPoint : new google.maps.Point(0, -29)
	});
	marker.setPosition(chennai);
	marker.setVisible(false);
	getUserLocation();
	google.maps.event.addListener(map, 'bounds_changed', function() {

		var bBox = getBB();
		$.ajax({
			url : '/getpoints',
			type : 'POST',
			data : JSON.stringify(bBox),
			contentType : 'application/json; charset=utf-8',
			dataType : 'json',
			async : false,
			success : function(msg) {
				addPointsToMap(msg);
			}
		});
		//alert("dragged");
	});

	google.maps.event.addListener(map, 'click', function(event) {

		console.log("zoom:" + map.getZoom());
		marker.setVisible(true);
		if (map.getZoom() >= 14 && map.getZoom() <= 18) {
			var lat = event.latLng.lat();
		    var lng = event.latLng.lng();
		    //var coords = [lng, lat];
			var jsonData = {"lat":lat,"lng":lng}
			marker.setPosition(event.latLng);
		    //console.log(JSON.stringify(coords));
			var boxText = document.createElement("div");
						boxText.innerHTML = '<div style="width:280px;height:25px;"><a id="request-help-map" class="request-help" href="#" style="padding:5px;font-size:1.3em;width:120px;float:left;text-align:center;">Request Help</a><a id="offer-help-map" class="offer-help" href="#" style="padding:5px;font-size:1.3em;width:120px;float:left;text-align:center;">Offer Help</a></div>' //'<iframe src="pdf-form.html"></iframe>';
						var myOptions = {
							content : boxText,
							disableAutoPan : false,
							alignBottom : true,
							pixelOffset : new google.maps.Size(-51, -52),
							zIndex : null,
							infoBoxClearance : new google.maps.Size(1, 1),
							isHidden : false,
							pane : "floatPane",
							enableEventPropagation : false
						};
						if (typeof infoBubble !== "undefined")
							infoBubble.close();
						infoBubble = new InfoBox(myOptions);
						infoBubble.open(map,marker);
						google.maps.event.addListener(infoBubble,'closeclick',function(){
							marker.setVisible(false); //removes the marker
							// then, remove the infowindows name from the array
						});
						openBubbleEvent = google.maps.event.addListener(infoBubble, 'domready', function () {
						var a = document.getElementById("request-help-map");
						a.onclick = function() {showRequestHelp(); return false;}
						var b = document.getElementById("offer-help-map");
						b.onclick = function() {showOfferHelp(); return false;}
						});

		}
	});
	var a = document.getElementById("request-help");
	a.onclick = function() {getUserLocation();showRequestHelp(); return false;}
	var b = document.getElementById("offer-help");
	b.onclick = function() {getUserLocation();showOfferHelp(); return false;}
}

function getUserLocation() {
	if (navigator.geolocation) {
		navigator.geolocation
				.getCurrentPosition(
						function(position) {
							var userLocation = new google.maps.LatLng(
									position.coords.latitude,
									position.coords.longitude);
							if (allowedBounds.contains(userLocation)) {
								userLocationMarker = new google.maps.Marker({
									position : userLocation,
									map : map,
									icon : getIcon('user'),
									optimized : false
								});
							} else {
								alert("Sorry, your location is outside Tamilnadu. Please click on the map to choose location.");
								map.setCenter(chennai);
								hideTopMenu();
								return;
							}
							map.setCenter(userLocation);
							marker.setPosition(userLocation);

						},
						function(error) {
							alert(
									"Sorry, something went wrong. Check to see if location services are enabled. You can also click on a location and add request/offer help.",
									error);
									hideTopMenu();
						}, {
							timeout : 10000,
							maximumAge : 600000,
							enableHighAccuracy : true
						});
	} else {
		alert("Sorry, geolocation is not supported by your browser.");
	}
}

google.maps.event.addDomListener(window, 'resize', function() {
	google.maps.event.trigger(map, 'resize');
});

var parcelPoints;
function addPointsToMap(json) {
map.data.forEach(function(feature) {
map.data.remove(feature)
});
data = json;
if (typeof dataListenEvent !== "undefined")
google.maps.event.removeListener(dataListenEvent);
parcelPoints = map.data.addGeoJson(data["allpoints"]);

dataListenEvent = map.data.addListener('click', function(event)
				{
					var objID = event.feature.getProperty("id");
					marker.setPosition(new google.maps.LatLng(event.feature.getGeometry().get().lat(), event.feature.getGeometry().get().lng()));
					marker.setVisible(true);
					if (typeof objID !== "undefined")
						getInfo(objID);
					//event.feature.get
				});

map.data.setStyle(function(feature) {
var color;
var check = feature.getProperty("type");
if (typeof check !== "undefined" && check==="Offering") {
color = 'green';
return ({
icon: {
path: google.maps.SymbolPath.CIRCLE,
fillColor: color,
strokeWeight: 0,
fillOpacity: 1,
scale: 5
}
});

}
else {
color = 'red';
return ({
icon: {
path: google.maps.SymbolPath.CIRCLE,
fillColor: color,
strokeWeight: 0,
fillOpacity: 1,
scale: 5
}
});
}
});

}

function showRequestHelp()
{
if (typeof openBubbleEvent === "undefined")
		google.maps.event.removeListener(openBubbleEvent);

$.ajax({
				url : '/requesthelp',
				type : 'GET',
				//data : JSON.stringify(jsonData),
				contentType : 'application/json; charset=utf-8',
				dataType : 'html',
				success : function(msg) {infoBubbleHelp(msg,marker);}
			});
}
function showOfferHelp()
{
if (typeof openBubbleEvent === "undefined")
		google.maps.event.removeListener(openBubbleEvent);

$.ajax({
				url : '/offerhelp',
				type : 'GET',
				//data : JSON.stringify(jsonData),
				contentType : 'application/json; charset=utf-8',
				dataType : 'html',
				success : function(msg) {infoBubbleHelp(msg,marker)
				}
			});
}
function infoBubbleHelp(msg,location)
{
	var boxText = document.createElement("div");
	boxText.innerHTML = msg //'<iframe src="pdf-form.html"></iframe>';
	var myOptions = {
		content : boxText,
		disableAutoPan : false,
		alignBottom : true,
		pixelOffset : new google.maps.Size(-51, -52),
		zIndex : 99999,
		infoBoxClearance : new google.maps.Size(1, 1),
		isHidden : false,
		pane : "floatPane",
		enableEventPropagation : false
	};
	if (typeof infoBubble !== "undefined")
		infoBubble.close();
	infoBubble = new InfoBox(myOptions);
	infoBubble.open(map,location);
	google.maps.event.addListener(infoBubble,'closeclick',function(){
							marker.setVisible(false); //removes the marker
							// then, remove the infowindows name from the array
						});
	marker.setVisible(true);


}

function getInfo(id)
{
	$.ajax({
				url : '/showinfo?id='+id,
				type : 'GET',
				//data : JSON.stringify(jsonData),
				contentType : 'application/json; charset=utf-8',
				dataType : 'html',
				success : function(msg) {infoBubbleHelp(msg,marker);}
			});
}

function hideTopMenu()
{
	$( "#top-menu" ).hide();
	$( "#outside-tn" ).show();

}
