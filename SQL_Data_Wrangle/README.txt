README
	P2: OpenStreetMap Data Wrangle
	Justin "Roy" Garrard

LOCATION:
	https://www.openstreetmap.org/export#map=10/43.6072/-116.3651

	A collection of six Southwestern Idaho cities, the region where
	I've spent most of my life.

FILES:
	README.txt-	
		You are here.

	idaho_sw.xml-
		The OSM data in XML format.

	OpenStreetMap_Data_Wrangling.ipynb-	
		A Jupyter Notebook where the conversion, cleaning, and query
		code was developed.

	OSM_xml_to_csv.py-
		A Python script that converts an OSM XML file into CSV files.

	OSM_csv_to_sql.py-
		A Python script that converts generated CSV files into a 
		SQLite database. Does not currently have queries built in
		(queries were performed in the Jupyter Notebook).

	street_cleaning.py-
		A collection of functions used by OSM_xml_to_csv.py.

	OSM_Project.md-
		The writeup for this project, as a .md file.

	OSM_Project.pdf-
		The writeup for this project, as a .pdf file.
