
CREATE TABLE "covers" (
	"id"	INTEGER NOT NULL,
	"book_name"	TEXT NOT NULL,
	"file_name"	TEXT NOT NULL,
	"url"	TEXT NOT NULL,
	"product_id" INTEGER NOT NULL UNIQUE,
	
	PRIMARY KEY("id" AUTOINCREMENT)
);

