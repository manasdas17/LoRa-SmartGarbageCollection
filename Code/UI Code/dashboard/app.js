var express 		= require('express');
var bodyParser 		= require('body-parser');
var cookieParser	= require('cookie-parser')
var path 			= require('path');
var session 		= require('express-session');
var fs 				= require('fs');
var logger 			= require('morgan');
var UglifyJS		= require('uglify-js');

var HTTPS_HOST 	= process.env.HOST || '127.0.0.1';
var HTTPS_PORT 	= process.env.PORT || 4000;
var mapHomePageresult = UglifyJS.minify(
					["./public/javascript/src/mapHomePage.js","./public/javascript/src/pubnub-3.16.5.min.js"],
					 {
						mangle: true,
						compress: {
							sequences: true,
							dead_code: true,
							conditionals: true,
							booleans: true,
							unused: true,
							if_return: true,
							join_vars: true,
							drop_console: false
						}
					});

fs.writeFile("./public/javascript/lib/map.min.js", mapHomePageresult.code, function(err) {
    if(err) {
        console.log(err);
    } else {
        console.log("mapHomePage File was successfully minified and saved.");
    }
});

var app = express();

app.use(logger('dev'));
app.use(cookieParser());
app.use(bodyParser.json());
app.use(bodyParser.text());
app.use(bodyParser.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));

app.use(session({ 
	secret: 'example',
		cookie:{
			maxAge:86400000
		},
		resave: false,
		saveUninitialized: true
}));

app.set("view engine","ejs")
app.set('views', __dirname + '/views')
app.set('views', path.join(__dirname, 'views'));

require('./routes/routes.js')(app);

app.listen(HTTPS_PORT);