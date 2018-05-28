var util 			= 	require('util');
var express 		= 	require('express');
var bodyParser 		= 	require("body-parser");
var crypto 			= 	require('crypto');
var path 			= 	require("path");
var session 		= 	require("express-session");

var pubnub = require("pubnub")({
    ssl           : true,  // <- enable TLS Tunneling over TCP
    
    publish_key   : "pub-c-002fbba1-6de1-410b-8c9e-ff75720aaa49",
    subscribe_key : "sub-c-62fed8bc-2d10-11e8-a27a-a2b5bab5b996"
    //publish_key   : "pub-c-002fbba1-6de1-410b-8c9e-ff75720aaa49",
    //subscribe_key : "sub-c-62fed8bc-2d10-11e8-a27a-a2b5bab5b996"
});

module.exports = function (app) {

	function checkSignIn(req, res, next ){
	    if(req.session.sessId){
	        next();     //If session exists, proceed to page
	    } else {
	        var err = new Error("Not logged in!");
	    	res.redirect('/');
	    }
	};

/////////////////////////////
// GET/POST PAGE RENDERING //
/////////////////////////////

/*
{"binId" : 1,"binData" : {"fillLevel" : 39,"batteryLevel" : 43, "timeStamp":"21/3 21:13"}}
*/

	app.get('/', function (request, response, next) {
		response.redirect('/index.html')
	});

	app.get('/mapDashboard', function (request, response, next) {
		response.render('mapDashboard');
	});

	app.get('/keysfetch',function (request, response, next) {
		
		function reverseString(str) {
		    return str.split('').reverse().join('');
		}

		var mapboxAccessToken = reverseString('pk.eyJ1Ijoic3VyeWFpZ29yIiwiYSI6ImNqZjE1eWRkbzB1YzUzM3Foczd2eTd0YXAifQ.uCMhviS_QNT6uLXeBmxk9Q');
		var pubnubPublishKey = reverseString('pub-c-002fbba1-6de1-410b-8c9e-ff75720aaa49');
		var pubnubSubscribeKey = reverseString('sub-c-62fed8bc-2d10-11e8-a27a-a2b5bab5b996');
		
		var mdat = new Buffer(mapboxAccessToken)
		var ppk = new Buffer(pubnubPublishKey)
		var psk = new Buffer(pubnubSubscribeKey)
		
		response.status(200).send({
			"MDAT":mdat.toString('base64'),
			"PPK":ppk.toString('base64'),
			"PSK":psk.toString('base64')
		})
	});

	app.get('/logout', function (request, response, next) {
		request.session.destroy(function(err){
			if(err){
				console.log(err);
			}else{
				response.redirect('/');
			}
		});
	});

	app.post("/login", function (request, response) {
		var body = request.body;
		var usersessId = body.username;
		var hash = crypto.createHash('md5').update(body.password).digest("hex");
		var postVars = {username: body.username, password: hash};
		console.log('login '+body.username, hash);
		if(body.username === "user" && hash === "ee11cbb19052e40b07aac0ca060c23ee"){
			response.redirect('/mapDashboard');	
		}
		else{
			response.redirect('/index.html')
		}
	});
	
	app.post("/register", function (request, response) {
	    response.redirect('/index.html');
	});
};
