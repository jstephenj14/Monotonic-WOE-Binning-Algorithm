# Monotonic-WOE-Binning-Algorithm

_This algorithm is based on the excellent paper by Mironchyk and Tchistiakov (2017) named "Monotone	optimal	binning	algorithm	for	credit risk	modeling". Any mistakes or shortcomings of the Python code are mine alone and I'd appreciate feedback on these possible errors_

The weight-of-evidence (WOE) method of evaluating strength of predictors is an understated one in the field of analytics.
While it is standard fare in credit risk modelling, it is under-utilized in other settings though its formulation makes it
generic enough for use in other domains too. The WOE method primarily aims to bin variables into buckets that deliver the most
information to a potential classification model. Quite often, WOE binning methods measure effectiveness of such bins using Information Value
or IV. For a more detailed introduction to WOE and IV, [this article](http://ucanalytics.com/blogs/information-value-and-weight-of-evidencebanking-case/)
is a useful read. 

In the world of credit risk modelling, regulatory oversight often requires that the variables that go into models
are split into bins 

- whose weight of evidence (WOE) values maintain a monotonic relationship with the 1/0 variable (loan default or not default for example.)
- are reasonably sized and large enough to be respresentative of population segments, and
- maximize the IV value of the given variable in the process of this binning. 

To exemplify the constraints such a problem, consider a simple dataset containing age and a default indicator (1 if defaulted, 0 if not).
The following is a possible scenario in which the variable is binned into three groups in such a manner that their WOE values decrease monotomically
as the ages of customers increase. 

<a href="https://drive.google.com/uc?export=view&id=10NHDsJQbZRgO3QQGK2dMkoAmzJxtQR_A"><img src="https://drive.google.com/uc?export=view&id=10NHDsJQbZRgO3QQGK2dMkoAmzJxtQR_A" style="width: 500px; max-width: 100%; height: auto" title="WOE Table" /></a>

The WOE is derived in such a manner that as the WOE value increases, the default rate decreases. So we can infer 
that younger customers are more likely to default in comparison to older customers.

Arriving at the perfect bin cutoffs to meet all three requirements discussed earlier is a non-trivial exercise. Most statistical software
provide this type of optimal discretization of interval variables. R's [smbinning package](https://cran.r-project.org/web/packages/smbinning/smbinning.pdf)
and SAS' [proc transreg](https://statcompute.wordpress.com/2017/09/24/granular-monotonic-binning-in-sas/) are two such examples. To my knowledge, Python's solutions to this problem are fairly sparse. 

My solution here takes two columns of data: a 1/0 variable and the variable to be binned. It returns a binned variable along with respective WOE values conditioned on user-defined thresholds on minimum possible bin size, minimum
number of defaults in each bin and the maximum p-value allowed for a possible t-test in means between adjacent bins.

I hope my attempt here serves as a helpful stop-gap for someone looking to perform risk modelling in Python using WOE methods.


