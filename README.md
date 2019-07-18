# PIG_Project
General instructions:
1. 	The python script for the toolbox is contained in the folder and is called "init_script.py".
2. 	The original points of the tracked birds are in the folder and are called "points.shp".
3. 	The original metadata of the birds is called "Eagle owl Reinhard Vohwinkel MPIO-reference-data.csv".
4. 	The corine landcover in shapefile as well as a summary statistics table of it is stored in "landuse.gdb".
5. 	The toolbox is called "Toolbox_bubo_bubo.tbx"
6.	The results of a computation with all birds (4-8 hours computation time) is also contained in the folder, it is called  "all_the_birds_results"
7. 	While running the toolbox, it is important to create a new folder like the example "all_the_birds_results" and use this as the  workspace.

Proposed selections for testing the toolbox, as the total running time takes 4-8 hours, depending on the used hardware:
1.	 Lower amount of points: Bird-IDs 1750 and 1751. These owls are a couple. Estimated computation time: 2-4 minutes, depending on the used hardware.
2.  	Higher amount of points: Bird-IDs 3892 and 3893. These owls are a couple. Estimated computation time: 6-10 minutes, depending on the used hardware.

Methodology:
1.	Segregate the data of all birds.  
2.	For each bird:  
i.	Find the buffer of all points and join them  
ii.	Take only the Dissolved Buffer with a threshold area  
iii.	Extract all the points from the buffers in (ii)  
iv.	Calculate the Minimum Bounding Geometry for the points from (iii)  
v.	Do (iv) for all the inputs given by the user in (3) 
3.	Calculate the difference in territory (Minimum Bounding Geometry) based on:    
i.	Gender: Male or Female  
	a.	Join the table information   
	b.	Use selected for calculating territory  
ii.	Seasons:  
	a.	Spring: March, April, May     
	b.	Summer: June, July, August   
	c.	Autumn: September, October, November  
	d.	Winter: December, January, February  
iii.	Corine Landcover:  
	a.	Take the territory from (2) and extend by creating a buffer  
	b.	Extract the Landcover taking (a) as input mask  
	c.	Return the extracted Landcover  
4.	Comparison based on User Choice.  
