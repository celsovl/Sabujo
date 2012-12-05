$(function() {

	(function() {

		var siginst = sigma.init($('#sig').get(0));

		var Sabujo = {
			getWebsiteInfo: function(domain, func) {
				$.get('/services/websiteinfo/' + domain, function(data) {
					if (data) func(data);
				});
			},
			getTopHeaders: function(domain, func) {
				$.get('/services/topheaders/' + domain, function(data) {
					if (data) func(data);
				});
			},
			typeaheadDomain: function(query, func) {
				$.get('/services/typeaheaddomain/' + encodeURIComponent(query), function(data) {
					if (data) func(data);
				});
			},
			getImages: function(urlId, func) {
				$.get('/services/domain/images/' + urlId, function(data) {
					if (data.success)
						func(data.success);
				});
			}
		};

		function View(el, website, siginst) {
			var self = this;

			self.mainwebsite = website;
			self.websites = {};
			self.websites[website.domain] = website;
			self.el = el;
			self.siginst = siginst;

			self.siginst.drawingProperties({
				defaultLabelColor: '#ccc',
				font: 'Arial',
				edgeColor: 'source',
				defaultEdgeType: 'curve'
			}).graphProperties({
				minNodeSize: 3,
				maxNodeSize: 10
			});

			function select(website) {
				var html = [], node;

				html.push('<ul class="unstyled">');
				html.push('<li>' + website.details.links + ' pagina(s)</li>');
				html.push('<li>' + website.details.foreignLinks + ' link(s) para outro(s) site(s)</li>');
				html.push('<li>' + website.details.images + ' imagem(ns)</li>');
				html.push('</ul>');

				self.siginst.draw();

				self.siginst.iterNodes(function(n) {
					node = n;
				}, [website.domain]);

				$('#popuppos').popover('destroy');

				$('#popuppos').css({
					position: 'absolute',
					left: node.displayX - 5 + $('#sig').get(0).offsetLeft,
					top: node.displayY + 5 + $('#sig').get(0).offsetTop
				}).popover({
					animation: true,
					html: true,
					placement: 'bottom',
					title: website.domain,
					content: html.join('\n')
				});

				$('#popuppos').popover('show');
				$('#domain').text(website.domain).attr('href', '/domain/' + website.domain);
				self.loadTopHeaders(website);
				self.loadImages(website);
			}


			function loadTopHeaders(website) {
				Sabujo.getTopHeaders(website.domain, function(data) {
					if (!data.success) {
						$('#domainHeaders').html('');
						return;
					}

					data = data.success;
					html = [];

					for (var i = 0; i < Math.ceil(data.length/10); i++) {
						html.push("<div class='span4'>");
						html.push("<table class='table table-condensed table-hover'>");
						for (var j = i*10; j < Math.min((i+1)*10, data.length); j++) {
							var d = data[j];
							html.push("<tr><td><a class='btn btn-link btn-small' href='/url/" + d.urlId + "'>" + d.header + "</a></td></tr>");
						}
						html.push("</table>");
						html.push("</div>");
					}
					$('#domainHeaders').html(html.join(' '));
				});
			}

			function loadImages(website) {
				Sabujo.getImages(website.domain, function(data) {
					var lines = [];
					for (var i = 0; i < data.length; i++) {
						var line = data[i];
						lines.push("<li class='span2'><a class='thumbnail' href='http://" + line.domain + line.path + "'><img src='/imgdb/" + line.urlId + "'/></a></li>")
					}
					$('#images').html(lines.join(''));
				});
			}

			function init() {
				self.siginst.emptyGraph();
				$('#popuppos').popover('destroy');

				_.each(_.values(self.websites), function(w) {
					self.add(w);
				});

				self.siginst.bind('downnodes', function(e) {
					$('#popuppos').popover('destroy');
				});

				self.siginst.bind('upnodes', function(e) {
					var domain = e.content[0];
					if (self.websites[domain] === undefined) {
						Sabujo.getWebsiteInfo(domain, function(website) {
							self.add(website);
							self.select(website);
						});
					} else {
						self.select(self.websites[domain]);
					}
				});
			}

			function color() {
				return '#00A0B0';
			}

			function add(website) {
				self.websites[website.domain] = website;
			
				try {
					self.siginst.addNode(website.domain, {
						label: website.domain,
						color: self.color(),
						x: self.getX(website.domain),
						y: self.getY(website.domain),
						size: website.details.links,
						forceLabel: true
					});
				} catch (e) {}

				// Add nodes
				var linkedBy = _.pairs(website.linkedBy);

				_.each(linkedBy, function(pair) {
					var website = pair[0];
					var size = pair[1];
					try {
						self.siginst.addNode(website, {
							label: website,
							color: self.color(),
							x: self.getX(website),
							y: self.getY(website),
							size: size,
							forceLabel: true
						});
					} catch (e) {}
				});
				
				
				// Add edges
				_.each(linkedBy, function(pair) {
					var link = pair[0];
					try {
						self.siginst.addEdge(
							link+'->'+website.domain,
							link,
							website.domain);
					} catch (e)	{
						// node doesn't exists yet
					}
				});

				self.siginst.draw();
			}

			function getX(website) {
				return $(self.el).width()*Math.random();
			}

			function getY(website) {
				return $(self.el).height()*Math.random();
			}

			self.add = add;
			self.init = init;
			self.color = color;
			self.getX = getX;
			self.getY = getY;
			self.select = select;
			self.loadTopHeaders = loadTopHeaders;
			self.loadImages = loadImages;
		}
		
		$('.search-query').typeahead({
			minLength: 3,
			source: function(query, process) {
				var that = this;
				Sabujo.typeaheadDomain(query, function(data) {
					if (data.options)
						process(data.options);
				});
			},
			updater: function(domain) {
				Sabujo.getWebsiteInfo(domain, function(website) {
					var view = new View($('#sig').get(0), website, siginst);
					view.init();
					$('#domain').text(website.domain).attr('href', '/domain/' + website.domain);
					view.loadTopHeaders(website);
					view.loadImages(website);
				});
			}
		});

	})();
	
});
