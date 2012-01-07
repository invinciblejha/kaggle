Model
=====

X
-
Counts for all values of all columns
    Gives lots of X variables
    
    #claims could be a separate category. Maxes at 43/year

Models
------    
Separate models for 
    Sex
    Age group

Different groups have different base likelyhood of needing to go to hospital. This should 
be independent of observed behaviours

We look for signs of impending hospitalisation in each group
    
Classification / Abnormal behavior model
----------------------------------------
Healthy people tend not to go to hospital so try to detect signs of unheathiness
  
Cascading classifiers

    All     => DIH ==  0 | DIH > 0
    DIH > 0 => DIH ==  1 | DIH > 1
    DIH > 1 => DIH ==  2 | DIH > 2 
    DIH > 2 => DIH ==  4 | DIH > 4
    DIH > 4 => DIH ==  8 | DIH > 8 
    DIH > 8 => DIH == 16 | DIH > 16     