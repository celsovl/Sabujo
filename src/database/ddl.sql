drop table if exists processQueue;
drop table if exists taskQueue;

create table if not exists taskQueue (
	id int auto_increment primary key,
	url varchar(4096) not null,
	sha1Url binary(20) not null,
	processed bool not null,
	constraint tmpUrl unique (sha1Url)
);

create table if not exists processQueue (
	id int auto_increment primary key,
	url varchar(4096) not null,
	sha1Url binary(20) not null,
	processed bool not null,
	request text not null,
	response text not null,
	data blob null,
	constraint tmpUrl unique (sha1Url)
);

drop table if exists urlImage;
drop table if exists urlDocument;
drop table if exists urlHeader;
drop table if exists urlToUrl;
drop table if exists url;
drop table if exists domain;

create table if not exists domain (
	id int auto_increment primary key,
	name varchar(600),
	constraint domainName unique (name)
);

create table if not exists url (
	id int auto_increment primary key,
	domainId int not null,
	path varchar(4096) not null,
	sha1Path binary(20) not null,
	mime varchar(100) null,
	type int null,
	constraint urlToDomain foreign key (domainId)	references domain(id),
	constraint urlPath unique (sha1Path, domainId)
);

create table if not exists urlToUrl (
	referenceId int not null,
	referencedId int not null,
	text varchar(4096) null,
	constraint urlToUrlPk primary key (referenceId, referencedId),
	constraint referenceUrl foreign key (referenceId) references url(id),
	constraint referencedUrl foreign key (referencedId) references url(id)
);

create table if not exists urlDocument (
	urlId int not null primary key,
	title varchar(4096) null,
	description varchar(4096) null,
	text text not null,
	textHtml text not null,
	constraint documentToUrl foreign key (urlId) references url(id)
);

create table if not exists urlHeader (
	urlId int not null,
	text text not null,
	constraint headerToUrl foreign key (urlId) references url(id)
);

create table if not exists urlImage (
	urlId int not null primary key,
	image blob not null,
	constraint imageToUrl foreign key (urlId) references url(id)
);