console.log("loading logon.js");

/***************************************
 *				LOGIN STUFF 
 ***************************************/

// instanciate firebase
var myFirebaseRef = new Firebase("https://alfr3d.firebaseio.com/");

window.onkeydown = function (e) {
    var code = e.keyCode ? e.keyCode : e.which;
    if (code === 27) { //esc key
        alert('There is no way out');
    } else if (code === 13) { //enter key

		myFirebaseRef.authWithPassword({
			email    : document.getElementById('user_id').value,
			password : document.getElementById('pass_wd').value
		}, function(error, authData) {
			if (error) {
				console.log("Login Failed!", error);
				deny();
			} else {
				console.log("Authenticated successfully with payload:", authData);
				login(authData.password.email.replace(/@.*/, ''));
			}
		})

	}
};

function deny() {
	console.log("DENIED")
	document.getElementById('section').style.display = 'none';

	img.src = '../img/denied.png';	
	img.onload = function() {
		init();
		window.onresize = init;
	};
};

// Tests to see if /users/<userId> has any data. 
function login(user_id) {
	console.log('existance check...');
	document.getElementById('section').style.display = 'none';
	myFirebaseRef.child("users/"+user_id+"/name").once('value', function(snapshot) {
		exists = (snapshot.val() !== null);
		console.log("user exists:"+exists);
		userExistsCallback(user_id, exists);
	});		
};

function userExistsCallback(user_id, exists) {
	if (exists) {
		welcome(user_id);
 	} else {
 		// Create user
 		new_user(user_id);
 	}
}

/***************************************
 *	 			GLITCH STUFF 
 ***************************************/

// ready canvas for glitch
var canvas = document.getElementById('canvas')
  , context = canvas.getContext('2d')
  , img = new Image()
  , w
  , h
  , offset
  , glitchInterval;

var init = function() {
	clearInterval(glitchInterval);
	canvas.width = w = window.innerWidth;
	offset = w * .1;
	canvas.height = h = img.height;
	glitchInterval = setInterval(function() {
		clear();
		//context.drawImage(img, window.innerWidth/2-img.width/2, 0);
		setTimeout(glitchImg, randInt(250, 1000));
		setTimeout(cleanImg, randInt(500, 1000));
	}, 500);
};

var clear = function() {
	context.rect(0, 0, w, h);
	//context.fill();
	context.clearRect ( 0 , 0 , canvas.width, canvas.height );
};
    
var glitchImg = function() {
	for (var i = 0; i < randInt(1, 13); i++) {
		var x = Math.random() * w;
		var y = Math.random() * h;
		var spliceWidth = w - x;
		var spliceHeight = randInt(5, h / 3);
		context.drawImage(img, 0, y, spliceWidth, spliceHeight, x, y, spliceWidth, spliceHeight);
		context.drawImage(img, spliceWidth, y, x, spliceHeight, 0, y, x, spliceHeight);
	}
};

var cleanImg = function() {
	context.drawImage(img, window.innerWidth/2-img.width/2, 0);
};

var randInt = function(a, b) {
	return ~~(Math.random() * (b - a) + a);
};



/***************************************
 *	 			WELCOME PAGE 
 ***************************************/

 function welcome(user_id) {
	myFirebaseRef.child("users/"+user_id+"/name").once('value', function(snapshot) { 
		var name = snapshot.val();
	});	

	console.log("Welcome back "+name);

	// write alfr3d_url at the top of the page
	myFirebaseRef.child("users/"+user_id+"/location").once('value', function(snapshot) { 		
		console.log('location: '+snapshot.val());

		ref = snapshot.val();
		ret = '';
		ret_counter = 0;

		write();

		function write() {
			var timer = setTimeout(function(){
				ret+=snapshot.val().charAt(ret_counter);
				ret_counter++;
				console.log(ret);
				document.getElementById('alfr3d_url').innerHTML = ret;			
				write();
			}, randInt(100, 300));
			if (ret_counter >= snapshot.val().length) {
				clearTimeout(timer); 
				window.location.href = "http://"+snapshot.val()+"/alfr3d.io/main.html";
			}
		}
	});	
 };

 function new_user(user_id) {
 	// TO-DO:
 	console.log("Creating new user profile for "+user_id);
 };

 function drawRoomCtrls() {
 	// ready canvas for Dummy image
	var canvas = document.getElementById('canvas')
		, context = canvas.getContext('2d')
		, img = new Image();

	img.src = '../img/Alfr3d-Room.png';
	console.log("image found");

	canvas.width = w = window.innerWidth;
	canvas.height = h = img.height;	

	img.onload = function() {
		console.log("image loaded");
		context.drawImage(img, window.innerWidth/2-img.width/2, 0);
	}

 }
