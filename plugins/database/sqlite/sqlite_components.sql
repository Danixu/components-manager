CREATE TABLE IF NOT EXISTS
Categories (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Parent INTEGER NOT NULL,
	Name TEXT NOT NULL,
	Expanded BOOLEAN,
	Template TEXT DEFAULT NULL,
	FOREIGN KEY (Parent)
    REFERENCES Categories(ID)
    ON DELETE CASCADE
);

/* Creating root Category to allow Foreing Keys without error */
INSERT INTO 
Categories
	SELECT -1, -1, "Root category (to be ignored)",	0, null 
		WHERE NOT EXISTS(
			SELECT 1 FROM Categories WHERE id = -1
		)
;

CREATE INDEX IF NOT EXISTS
	Categories_parent
ON
	Categories(Parent ASC);


CREATE TABLE IF NOT EXISTS Components (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Category INTEGER NOT NULL,
	Template TEXT NOT NULL,
	FOREIGN KEY (Category)
    REFERENCES Categories(ID)
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS
	components_category
ON
	Components(Category ASC);


CREATE TABLE IF NOT EXISTS Components_data (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Component INTEGER NOT NULL,
	Field_ID INTEGER NOT NULL,
	Value TEXT NOT NULL,
	UNIQUE (
		[Component],
		[Field_ID]
	),
	FOREIGN KEY (Component)
    REFERENCES Components(ID)
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS
	components_data_component
ON
	Components_data(Component ASC);
	
	
CREATE TABLE IF NOT EXISTS Images (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Component_id INTEGER DEFAULT NULL,
	Category_id INTEGER DEFAULT NULL,
	Image BLOB NOT NULL,
	Imagecompression INTEGER DEFAULT 0,
	FOREIGN KEY (Component_id)
    REFERENCES Components(ID)
    ON DELETE CASCADE,
	FOREIGN KEY (Category_id)
    REFERENCES Categories(ID)
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS
	images_component_id
ON
	Images(Component_id ASC);
CREATE INDEX IF NOT EXISTS
	images_category_id
ON
	Images(Category_id ASC);


CREATE TABLE IF NOT EXISTS Files (
	ID INTEGER PRIMARY KEY AUTOINCREMENT,
	Component INTEGER NOT NULL,
	Filename TEXT(8) NOT NULL,
	Datasheet BOOLEAN DEFAULT 0,
	FOREIGN KEY (Component)
    REFERENCES Components(ID)
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS
	Files_component
ON
	Files(Component);

CREATE INDEX IF NOT EXISTS
	Files_datasheet
ON
	Files(Datasheet);

	
CREATE TABLE IF NOT EXISTS Files_blob (
	File_id INTEGER NOT NULL,
	Filedata BLOB NOT NULL, 
	Filecompression INTEGER DEFAULT 0,
	FOREIGN KEY (File_id)
    REFERENCES Files(ID)
    ON DELETE CASCADE
);