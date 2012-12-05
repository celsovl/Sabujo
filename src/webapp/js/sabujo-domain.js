$(function() {

	(function() {

		var Sabujo = {
			getPages: function(domain, func) {
				$.get('/services/domain/pages/' + encodeURIComponent(domain), function(data) {
					if (data.success)
						func(data.success);
				});
			},
			getLinks: function(domain, func) {
				$.get('/services/domain/links/' + encodeURIComponent(domain), function(data) {
					if (data.success)
						func(data.success);
				});
			}
		};

		Sabujo.getPages($('#domain').val(), function(data) {
			html = [];

			var remainder = data.length;
			while (remainder > 0) {
				html.push("<div class='row'>");
				for (var i = 0; i < 3 && remainder > 0; i++) {
					html.push("<div class='span4'>");
					html.push("<table class='table table-condensed table-hover table-bordered table-striped'>");
					for (j = 0; j < 5 && remainder > 0; j++) {
						var d = data[data.length-remainder];
						var description = "";
						if (d.description)
							description = "<p>" + d.description + "</p>";

						html.push("<tr><td><a class='btn btn-link btn-small' href='/url/" + d.urlId + "'>" + d.title + "</a>" + description + "</td></tr>");
						remainder--;
					}
					html.push("</table>");
					html.push("</div>");
				}
				html.push("</div>");
			}
			$('#domainPages').html(html.join(' '));
		});


		Sabujo.getLinks($('#domain').val(), function(data) {
			html = [];

			var remainder = data.length;
			while (remainder > 0) {
				html.push("<div class='row'>");
				for (var i = 0; i < 2 && remainder > 0; i++) {
					html.push("<div class='span6'>");
					html.push("<table class='table table-condensed table-hover table-bordered table-striped'>");
					for (j = 0; j < 5 && remainder > 0; j++) {
						var d = data[data.length-remainder];
						html.push("<tr><td><a class='btn btn-link btn-small' href='http://" + d.domain + d.path + "'>" + d.text + "</a></td></tr>");
						remainder--;
					}
					html.push("</table>");
					html.push("</div>");
				}
				html.push("</div>");
			}
			$('#domainLinks').html(html.join(' '));
		});

	})();

});
