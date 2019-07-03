# PIG_Project
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
