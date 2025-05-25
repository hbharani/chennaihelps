// GLOBAL VARIABLES
var map;
var infoBubble;
var infoBubbleHelp;
var marker;
var userlat, userlon;
var geocoder;
var bounds;
var directionsService;
var directionsDisplay;
var active_id;
var initialLocation;
var browserSupportFlag = new Boolean();
var chennai = new google.maps.LatLng(13.0839, 80.2700);

// Function to get current bounding box
function getBB() {
	bounds = map.getBounds();
	sw = bounds.getSouthWest();
	ne = bounds.getNorthEast();
	bb = [[sw.lng(), sw.lat()], [ne.lng(), sw.lat()], [ne.lng(), ne.lat()], [sw.lng(), ne.lat()], [sw.lng(), sw.lat()]];
	return bb;
}

// Function to get icon based on type
function getIcon(type) {
	if (type == "Requesting")
		return "/static/img/marker-images/image.png";
	else if (type == "Offering")
		return "/static/img/marker-images/image_green.png";
	else
		return "/static/img/marker-images/image.png"; // Default icon
}

// Function to initialize map
function initialize() {
	geocoder = new google.maps.Geocoder();
	var myOptions = {
		zoom : 10,
		mapTypeId : google.maps.MapTypeId.ROADMAP
	};
	map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	infoBubble = new InfoBubble({
		map : map,
		shadowStyle : 1,
		padding : 10,
		backgroundColor : '#333',
		borderRadius : 10,
		arrowSize : 20,
		borderWidth : 2,
		borderColor : '#ccc',
		disableAutoPan : true,
		hideCloseButton : false,
		arrowPosition : 50,
		arrowStyle : 0,
		maxHeight : 300
	});
	infoBubbleHelp = new InfoBubble({
		map : map,
		shadowStyle : 1,
		padding : 10,
		backgroundColor : '#333',
		borderRadius : 10,
		arrowSize : 20,
		borderWidth : 2,
		borderColor : '#ccc',
		disableAutoPan : true,
		hideCloseButton : false,
		arrowPosition : 50,
		arrowStyle : 0,
		maxHeight : 300
	});
	marker = new google.maps.Marker({
		map : map,
		title : "Drag Me",
		draggable : true,
		visible: false // Initially hidden
	});

	// Try W3C Geolocation method
	if (navigator.geolocation) {
		browserSupportFlag = true;
		navigator.geolocation.getCurrentPosition(function(position) {
			userlat = position.coords.latitude;
			userlon = position.coords.longitude;
			initialLocation = new google.maps.LatLng(userlat, userlon);
			map.setCenter(initialLocation);
			map.setZoom(15);
			//showUserLocation(); // Optionally show user's current location marker
		}, function() {
			handleNoGeolocation(browserSupportFlag);
		});
	}
	// Browser doesn't support Geolocation
	else {
		browserSupportFlag = false;
		handleNoGeolocation(browserSupportFlag);
	}

	google.maps.event.addListener(map, 'bounds_changed', function() {
		$.post("/getpoints", JSON.stringify(getBB()), function(data) {
			// Clear existing markers if needed (depends on how you manage markers)
			// For simplicity, let's assume we add new markers without clearing old ones for now.
			// This might lead to duplicate markers if not handled properly.
			if (data && data.features) {
				data.features.forEach(function(feature) {
					var pt = new google.maps.LatLng(feature.geometry.coordinates[1], feature.geometry.coordinates[0]);
					var marker = new google.maps.Marker({
						position : pt,
						map : map,
						icon : getIcon(feature.properties.type),
						title : feature.properties.type + " - Click for details"
					});
					google.maps.event.addListener(marker, "click", function() {
						getInfo(feature.properties.id, marker);
					});
				});
			}
		}, "json"); // Expect JSON response
	});

	// Listener for map click to place a new marker for request/offer
	google.maps.event.addListener(map, "click", function(event) {
        if (marker) {
            marker.setPosition(event.latLng);
			marker.setVisible(true);
        } else {
            marker = new google.maps.Marker({
                position: event.latLng,
                map: map,
				title : "Drag Me",
		        draggable : true,
            });
        }
        // Decide whether to show request or offer form.
        // Defaulting to request help form for now.
        showRequestHelp(marker);
    });
}

function handleNoGeolocation(errorFlag) {
	if (errorFlag == true) {
		// Geolocation service failed.
		initialLocation = chennai; // Default to Chennai
	} else {
		// Browser doesn't support geolocation.
		initialLocation = chennai; // Default to Chennai
	}
	map.setCenter(initialLocation);
	map.setZoom(10);
}


// Function to clear previous error messages
function clearFormErrors() {
    var errorSpans = document.querySelectorAll('.help-inline');
    errorSpans.forEach(function(span) {
        span.textContent = '';
    });
}

// Function to display errors (can be enhanced later)
function displayFormErrors(errors) {
    clearFormErrors(); // Clear previous errors
    if (errors && Array.isArray(errors)) {
        errors.forEach(function(err) {
            if (err.loc && err.loc.length > 1) {
                var fieldName = err.loc[1];
                var errorSpan = document.getElementById(fieldName + '_errors');
                if (errorSpan) {
                    errorSpan.textContent = err.msg;
                } else {
                    // Fallback for errors not tied to a specific field shown in the form
                    console.warn('Error span not found for field:', fieldName, 'Error:', err.msg);
                    // alert('Validation error for ' + fieldName + ': ' + err.msg); // Simple alert as fallback
                }
            } else if (err.msg) {
                 // General error message not specific to one field.
                alert('Error: ' + err.msg);
            }
        });
    } else if (typeof errors === 'string') {
        // For generic string error messages
        alert(errors);
    }
    // Ensure the infoBubble is shown with the form if it was closed or not correctly opened
    // This might need re-evaluation based on how infoBubbleHelp is used.
    // For now, the errors are displayed inline.
}


function uploadRequest(e) {
	if (!e) var e = window.event;
    if (e) { // Ensure e exists before trying to use it
		e.cancelBubble = true;
        if (e.stopPropagation)
	    	e.stopPropagation();
    }

	$('#lat').val(marker.getPosition().lat());
	$('#lng').val(marker.getPosition().lng());

    // Using the field ID for the service dropdown directly
	if ($( "#request_service" ).val() === "Select") {
		alert("Please choose request type.");
		return;
	}

    clearFormErrors(); // Clear previous errors before new submission
	var form_data = new FormData($('#upload-request')[0]);
	// console.log(form_data); // Keep for debugging if needed

	$.ajax({
		type : 'POST',
		url : '/uploadrequest', // This should match the FastAPI endpoint
		data : form_data,
		contentType : false, // For FormData
		dataType : 'text',    // Expecting plain text "1" or error string/JSON
		cache : false,
		processData : false, // For FormData
		success : function(msg, textStatus, jqXHR) {
            if (jqXHR.status === 200 && msg === "1") {
                alert("Your request is uploaded successfully, Please browse through available help in the map. Stay Safe!");
                if (typeof infoBubble !== "undefined") infoBubble.close();
                if (typeof infoBubbleHelp !== "undefined") infoBubbleHelp.close(); // Close help bubble too
                marker.setVisible(false);
                google.maps.event.trigger(map, 'bounds_changed');
            } else {
                // This case might occur if server returns 200 OK but not "1"
                // Or if server returns an error message as plain text with 200 OK
                console.error("Upload request success callback, but unexpected message:", msg);
                displayFormErrors("An unexpected error occurred. Server said: " + msg);
                // infoBubbleHelp might not be suitable if msg is not HTML
                // For now, using displayFormErrors.
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("Upload request error:", textStatus, errorThrown);
            var errorData = "An unknown error occurred.";
            if (jqXHR.responseJSON && jqXHR.responseJSON.detail) {
                // FastAPI validation errors
                errorData = jqXHR.responseJSON.detail;
                displayFormErrors(errorData);
            } else if (jqXHR.responseText) {
                // Other errors (e.g. HTML error page or plain text)
                // Attempt to parse if it's JSON, otherwise show as text
                try {
                    var parsedError = JSON.parse(jqXHR.responseText);
                    if (parsedError && parsedError.detail) {
                         errorData = parsedError.detail;
                    } else {
                        errorData = jqXHR.responseText.substring(0, 200); // Limit length
                    }
                } catch(e) {
                    errorData = jqXHR.responseText.substring(0, 200); // Limit length
                }
                displayFormErrors(errorData);
            }
            // The original code called infoBubbleHelp(msg, marker)
            // If the form is inside infoBubble, we need to ensure it stays open
            // or re-opens with the error messages.
            // For now, errors are displayed inline in the form.
        }
	});
};

function uploadOffer(e) { // Added 'e' parameter for consistency
	if (!e) var e = window.event;
    if (e) { // Ensure e exists
	    e.cancelBubble = true;
        if (e.stopPropagation)
		    e.stopPropagation();
    }

	$('#lat').val(marker.getPosition().lat());
	$('#lng').val(marker.getPosition().lng());

    // Using the field ID for the service dropdown directly
	if ($( "#offer_service" ).val() === "Select") {
		alert("Please choose offer type.");
		return;
	}
    
    clearFormErrors(); // Clear previous errors
	var form_data = new FormData($('#upload-offer')[0]);
	// console.log(form_data); // Keep for debugging if needed

	$.ajax({
		type : 'POST',
		url : '/uploadoffer', // This should match the FastAPI endpoint
		data : form_data,
		contentType : false, // For FormData
		dataType : 'text',    // Expecting plain text "1" or error string/JSON
		cache : false,
		processData : false, // For FormData
		success : function(msg, textStatus, jqXHR) {
            if (jqXHR.status === 200 && msg === "1") {
                alert("Your Offer is uploaded successfully, Please browse through people needing help in the map. Stay Safe!");
                if (typeof infoBubble !== "undefined") infoBubble.close();
                if (typeof infoBubbleHelp !== "undefined") infoBubbleHelp.close(); // Close help bubble too
                marker.setVisible(false);
                google.maps.event.trigger(map, 'bounds_changed');
            } else {
                console.error("Upload offer success callback, but unexpected message:", msg);
                displayFormErrors("An unexpected error occurred. Server said: " + msg);
            }
        },
        error: function(jqXHR, textStatus, errorThrown) {
            console.error("Upload offer error:", textStatus, errorThrown);
            var errorData = "An unknown error occurred.";
            if (jqXHR.responseJSON && jqXHR.responseJSON.detail) {
                // FastAPI validation errors
                errorData = jqXHR.responseJSON.detail;
                displayFormErrors(errorData);
            } else if (jqXHR.responseText) {
                try {
                    var parsedError = JSON.parse(jqXHR.responseText);
                    if (parsedError && parsedError.detail) {
                         errorData = parsedError.detail;
                    } else {
                        errorData = jqXHR.responseText.substring(0, 200);
                    }
                } catch(e) {
                    errorData = jqXHR.responseText.substring(0, 200);
                }
                displayFormErrors(errorData);
            }
        }
	});
};

// Function to show info bubble with request help form
function showRequestHelp(marker_obj) {
	$.get("/requesthelp", function(data) {
		infoBubbleHelp.setContent(data);
		infoBubbleHelp.open(map, marker_obj);
	});
}

// Function to show info bubble with offer help form
function showOfferHelp(marker_obj) {
	$.get("/offerhelp", function(data) {
		infoBubbleHelp.setContent(data);
		infoBubbleHelp.open(map, marker_obj);
	});
}

// Function to get info for a point
function getInfo(id, marker_obj) {
	active_id = id;
	$.get("/showinfo?id=" + id, function(data) {
		if (infoBubble) infoBubble.close();
		infoBubble.setContent(data);
		infoBubble.open(map, marker_obj);
	});
}

// Function to show user location
function showUserLocation() {
	var userMarker = new google.maps.Marker({
		position : new google.maps.LatLng(userlat, userlon),
		map : map,
		icon : "/static/img/user_loc.png",
		title : "Your Location"
	});
	// Optional: Add an info window for the user's location marker
	var userInfoWindow = new google.maps.InfoWindow({
		content: "This is you!"
	});
	google.maps.event.addListener(userMarker, 'click', function() {
		userInfoWindow.open(map, userMarker);
	});
}

// Function to hide top menu
function hideTopMenu() {
	$('#topmenu').hide();
	$('#showmenu').show();
}

// Function to show top menu
function showTopMenu() {
	$('#showmenu').hide();
	$('#topmenu').show();
}

$(document).ready(function() {
	initialize();
	$("#request-help").click(function() {
		hideTopMenu();
		marker.setPosition(map.getCenter());
		marker.setVisible(true);
		showRequestHelp(marker);
	});
	$("#offer-help").click(function() {
		hideTopMenu();
		marker.setPosition(map.getCenter());
		marker.setVisible(true);
		showOfferHelp(marker);
	});
	
	// Autocomplete for address fields if needed (example)
	// var addressInput = document.getElementById('address'); // Assuming 'address' is an ID in your form
    // if (addressInput) {
    //  var autocomplete = new google.maps.places.Autocomplete(addressInput);
    //  autocomplete.bindTo('bounds', map); // Bias search within map bounds
    // }
});

// Placeholder for infoBubbleHelp function if it was more complex
// function infoBubbleHelp(content, marker_obj) {
//    // This function was previously used to display HTML content in an info bubble.
//    // It's now primarily used by showRequestHelp and showOfferHelp.
//    // If it was also used for displaying error messages as HTML, that functionality
//    // has been replaced by displayFormErrors which updates inline error spans.
//    if (infoBubbleHelp) {
//        infoBubbleHelp.setContent(content);
//        infoBubbleHelp.open(map, marker_obj);
//    }
// }
