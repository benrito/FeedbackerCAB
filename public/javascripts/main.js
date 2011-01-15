var IMAGE_URL = "/static/images";

function getIEVersion(){var rv = -1;if (navigator.appName == 'Microsoft Internet Explorer'){var ua = navigator.userAgent;var re  = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");if (re.exec(ua) != null)rv = parseFloat( RegExp.$1 );}return rv;}
var ie = getIEVersion();

function Ajax(url, data) {
	this.url = url;
	this.data = data;
	this.type = 'GET';
	this.done = false;
	this.jquery_ajax = null;
	
	this.fetch = function(callback, errorCallback) {
		var obj = this;
		this.jquery_ajax = $.ajax({
			cache: false,
			url: this.url,
			data: this.data,
			type: this.type,
			obj: this,
			dataType: "text",
			timeout: 1000*60*60*1.5, // set timeout to 90 minutes
			success: function(msg, textStatus, xmlHttpRequest){
				try {
					eval('var msg_json='+msg);
					var result = msg_json;
					if (callback) {
						callback(result);
					}
				}
				catch(e) {
					//alert(e);
				}
			},
			error: function() {
				if (errorCallback) {
					errorCallback();
				}
			}
		});
	}
	
	this.abort = function() {
		if (!this.done) {
			this.jquery_ajax.abort();
		}
	}	
}

Ajax.submit = function (form, callback) {
	while (!form.is('form')) {
		form = form.parent();
	}
	var data = form.serialize();
	var type = form.attr('method').toUpperCase();
	var action = form.attr('action');
	var ajx = new Ajax(action, data);
	ajx.type = type;
	ajx.fetch(callback);
	return false;
};

function popup_window(url, name, width, height) {
	var settings = {"url": url, "name": name, "width": width, "height": height};
	var windowFeatures = "location=0,menubar=0,directories=0,toolbar=0,width=" + settings.width + ",height=" + settings.height;
	var centeredX, centeredY;
	if ($.browser.msie) {//hacked together for IE browsers
		centeredY = (window.screenTop - 120) + ((((document.documentElement.clientHeight + 120)/2) - (settings.height/2)));
		centeredX = window.screenLeft + ((((document.body.offsetWidth + 20)/2) - (settings.width/2)));
	}else{
		centeredY = window.screenY + (((window.outerHeight/2) - (settings.height/2)));
		centeredX = window.screenX + (((window.outerWidth/2) - (settings.width/2)));
	}
	var myWin = window.open(settings.url, settings.name, windowFeatures+',left=' + centeredX +',top=' + centeredY);
	myWin.focus();
	return myWin;
}

function pprint(object) {
	var output = '';
	for (property in object) {
	  output += property + ': ' + object[property]+"\n";
	}
	alert(output);
}

function preventbubble(e){
 if (e && e.stopPropagation) //if stopPropagation method supported
  e.stopPropagation()
 else
  event.cancelBubble=true
}
