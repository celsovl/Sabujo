$(function() {

	(function() {

		var heads = $('#heads');
		var text = $('#text');
		var title = $('#title');
		var images = $('#images');

		var Sabujo = {
			getDocument: function(urlId, func) {
				$.get('/services/url/document/' + urlId, function(data) {

					if (data.success)
						func(data.success);
				});
			},
			getImages: function(urlId, func) {
				$.get('/services/url/images/' + urlId, function(data) {
					if (data.success)
						func(data.success);
				});
			}
		};

		Sabujo.getDocument($('#urlId').val(), function(data) {
			title.attr('href', 'http://' + data.domain + data.path);
			title.html(data.title);
			$(data.textHtml).appendTo(text);
		});

		Sabujo.getImages($('#urlId').val(), function(data) {
			var lines = [];
			for (var i = 0; i < data.length; i++) {
				var line = data[i];
				lines.push("<li class='span2'><a class='thumbnail' href='http://" + line.domain + line.path + "'><img src='/imgdb/" + line.urlId + "'/></a></li>")
			}
			images.html(lines.join(''));
		});

	})();

});
