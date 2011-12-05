Goals
=====
Predict Y4 results.

TODO
====
* Compare regressing Y1=>Y2 and Y2=>Y3 to (Y1,Y2)=>Y3 to estimate importance of effects from 2 years ago
* Estimate random noise to see how import effects are
* Measure pcg diversity within years
* Repeat PrimaryConditionGroup analysis for ProcedureGroup
* Find correlation between PrimaryConditionGroup and ProcedureGroup

Techniques
==========
Stepwise regression/classification to find important variable. Naive Bayes?
LOWESS

References
==========
* http://www.quora.com/Netflix-Prize/Is-there-any-summary-of-top-models-for-the-Netflix-prize
* http://strataconf.com/strata2012/public/schedule/detail/22658
* Lasso and elastic-net regularized GLMs eg. "glmnet"
* Random Forests

Findings
========
Interesting how majority pcg tends to stick. Seems to be a reliable attribute.

python explore.py -x derived_Y1_Claims.csv:PrimaryConditionGroup -y  derived_Y2_Claims.csv:PrimaryConditionGroup
python explore.py -x derived_Y2_Claims.csv:PrimaryConditionGroup -y  derived_Y3_Claims.csv:PrimaryConditionGroup

Effects
-------
* DrugCount.csv

** DSFS seems to be an effect
** DrugCount seems to be an effect (more in Y3?)

* LabCount.csv

** 'Year' could be an effect 
** DSFS seems to be an effect
** LabCount seems to an effect (more in Y3?)

* Members.csv

** AgeAtFirstClaim seems to a strong effect for Y2 and Y3 
** Sex could be an effect 
** ClaimsTruncated seems to a strong effect
  
* derived_Claims.csv

** NumClaims is an effect

Counts
------
C:\dev\kaggle\heritage>python explore.py DaysInHospital_Y2.csv
Counts
max = 1
min = 1
mean = 1.000000

C:\dev\kaggle\heritage>python explore.py DaysInHospital_Y3.csv
Counts
max = 1
min = 1
mean = 1.000000

C:\dev\kaggle\heritage>python explore.py DrugCount.csv
Counts
max = 36
min = 1
mean = 10.766612

C:\dev\kaggle\heritage>python explore.py LabCount.csv
Counts
max = 36
min = 1
mean = 4.172301

C:\dev\kaggle\heritage>python explore.py Members.csv
Counts
max = 1
min = 1
mean = 1.000000

C:\dev\kaggle\heritage>python explore.py Target.csv
Counts
max = 1
min = 1
mean = 1.000000

C:\dev\kaggle\heritage>python explore.py Claims.csv
Counts
max = 130
min = 1
mean = 23.619381

Providers
---------

Some patients see many provider. These are not necessarily the same patients who make many claims.

C:\dev\kaggle\heritage>python explore.py -p Claims.csv:ProviderID
get_counts_by_patient() Claims.csv : ProviderID column = 1

Summary "patient counts for Claims.csv : ProviderID":
len = 113000
min = 1
max = 50
mean = 6.901301
median = 5

Max patient (count) = 39601022
      321261:  15
     8068884:  13
     1762682:  10
     2623982:   6
     2330561:   5
     2056604:   4
     7859645:   3
     7625199:   3
     1471092:   3
     6734782:   3
     2294325:   3
     6758744:   2
     2383456:   2
     5925581:   2
     7867244:   2
     2577152:   2
     3580529:   2
     6969441:   2
     8486431:   2
     8964140:   2
       82837:   1
     3317868:   1
     7737626:   1
     5773569:   1
     6959871:   1
     6515906:   1
     3412203:   1
     5880528:   1
     2284632:   1
     9089169:   1
     4444494:   1
     6175934:   1
     1885316:   1
     7448223:   1
     7948136:   1
     8414648:   1
     9674576:   1
     1736768:   1
     8786900:   1
     4863320:   1
     5748825:   1
      123754:   1
     1023579:   1
     7519551:   1
     4897642:   1
     7089985:   1
      650597:   1
     6436849:   1
      740314:   1
     4474226:   1

Summary "patient totals for Claims.csv : ProviderID":
len = 113000
min = 1
max = 130
mean = 23.619381
median = 13

Max patient (total) = 2397235
     7053364: 126
     9331351:   4