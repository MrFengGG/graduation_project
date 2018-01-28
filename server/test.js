var config = {
	/*
	ip:"119.23.210.76",
	port:27017,
	db:'film'
	*/
	ip:"127.0.0.1",
	port:"27017",
	db:"test"
}
function getdbUrl(){
	return 'mongodb://'+config.ip+":"+config.port+'/'+config.db;
}
var MongoClient = require("mongodb").MongoClient;
MongoClient.connect(getdbUrl(), function(error, db){
		var db = db.db('test')
	    var col = db.collection("move");
		var p = col.find({"classification":/动作/}).toArray(function(err,doc){
		    console.log(doc.length);
		})
	});