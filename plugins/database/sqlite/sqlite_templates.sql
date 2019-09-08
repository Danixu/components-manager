CREATE TABLE IF NOT EXISTS
[Categories] (
	[ID] INTEGER PRIMARY KEY AUTOINCREMENT,
	[Parent] INTEGER NOT NULL,
	[[Name] TEXT NOT NULL,
	[Expanded] BOOLEAN DEFAULT 0,
	FOREIGN KEY ([Parent])
    REFERENCES [Categories]([ID])
    ON DELETE CASCADE
);

/* Creating root Category to allow Foreing Keys without error */
INSERT INTO 
[Categories]
	SELECT -1, -1, "Root category (to be ignored)", 0
		WHERE NOT EXISTS(
			SELECT 1 FROM [Categories] WHERE id = -1
		)
;

CREATE INDEX IF NOT EXISTS
	categories_parent
ON
	[Categories]([Parent] ASC);


CREATE TABLE IF NOT EXISTS [Templates] (
	[ID] INTEGER PRIMARY KEY AUTOINCREMENT,
	[Category] INTEGER NOT NULL,
	[Name] TEXT NOT NULL,
	FOREIGN KEY ([Category])
    REFERENCES [Categories]([ID])
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS
	templates_category
ON
	[Templates]([Category] ASC);
	
	
CREATE TABLE IF NOT EXISTS [Fields] (
	[ID] INTEGER PRIMARY KEY AUTOINCREMENT,
	[Template] INTEGER NOT NULL,
	[Label] TEXT NOT NULL,
	[Field_type] INT NOT NULL,
	[Order] INTEGER NOT NULL,
	FOREIGN KEY ([Template])
    REFERENCES [Templates]([ID])
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS
	fields_template
ON
	[Fields]([Template] ASC);


CREATE TABLE IF NOT EXISTS [Fields_data] (
	[ID] INTEGER PRIMARY KEY AUTOINCREMENT,
	[Field] INTEGER NOT NULL,
	[Key] TEXT NOT NULL,
	[Value] TEXT,
	UNIQUE (
		[Field],
		[Key]
	),
	FOREIGN KEY ([Field])
    REFERENCES [Fields]([ID])
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS
	items_data_field
ON
	[Fields_data]([Field] ASC);


CREATE TABLE IF NOT EXISTS [Values_group] (
	[ID] INTEGER PRIMARY KEY AUTOINCREMENT,
	[Name] TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS [Values] (
	[ID] INTEGER PRIMARY KEY AUTOINCREMENT,
	[Group] INTEGER NOT NULL,
	[Value] TEXT NOT NULL,
    [Order] INTEGER NOT NULL,
	FOREIGN KEY ([Group])
    REFERENCES [Values_group]([ID])
    ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS
	values_grp
ON
	[Values]([Group] ASC);