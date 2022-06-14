# SAX-ARM algorithm

Python implementation of the SAX-ARM algorithm from _Park et. al. (2019)_.

This implementation takes a Pandas dataframe as an input. The dataframe must contain a column `t` containing the different timestamps.

---

## Context

This algorithm mines association rules efficiently among the deviant events of multivariate time series. To do so, the algorithm combines two existing methods, namely the Symbolic Aggregate approXimation (SAX) from _Lin et. al. (2003)_ - a symbolic representation of time series - and the Apriori algorithm from _Agrawal et. al. (1996)_ - a data mining method which outputs all frequent itemsets and association rules from a transactional dataset.

The SAX-ARM algorithm can be applied to a single multivariate time series or multiple univariate time series if all individual time series share the same timestamps and have the same length. The core of the SAX-ARM algorithm comprises three main steps:

- **SAX**: transforms the time series into a symbolic representation.
  - **Normalization**. We use the Inverse normal transformation (INT algorithm to transform the sample distribution to a correct approximation of the normal distribution (see _Beasley et. al., 2009_).
  - **Piecewise Aggregate Approximation (PAA)**. The PAA is used as a dimensionality reduction technique (see _Keogh et. al. 2001_). The PAA approximates the data by segmenting the sequences into equi-length sections and recording the mean value of these sections.
  - **Discretization**. Given that the normalized time series have highly Gaussian distribution, we can simply determine the “breakpoints” that will produce a equal-sized areas under Gaussian curve. Once the breakpoints are computed, we can discretize a time series using the PAA representation: all PAA coefficients that are below the smallest breakpoint are mapped to the symbol _a_, all coefficients greater than or equal to the smallest breakpoint and less than the second smallest breakpoint are mapped to the symbol _b_, _etc_.
- **Symbol basket generation**: finds deviant events and creates transactional data structures. The SAX-ARM algorithm introduces a basket architecture that will store the deviant events discovered across all time series. A deviant event occurs when the value of a time series is represented with the first or last symbol of the given alphabet. Such events correspond to low-probability events (in the tail of the Gaussian distribution) and thus may be considered as anomalies or at least somewhat interesting events. A symbol basket is a list-like structure, in which, for a given time stamp, the deviant events - if any - of all time series are identified in the form `e = (i, symb)`, where `i` is the index of the time series and `symb` the symbol associated with the deviant event. Compared to _Park et. al._, our implementation discards empty symbol baskets as they have no practical use and are nothing but a waste of memory space.
- **ARM**: mines association rules in the symbol baskets using the Apriori algorithm. The Apriori algorithm was first introduced by _Agrawal et. al._. The objective of this algorithm is to mine association rules given a set of transactional data. This problem can be separated into two sub-problems: 1) computing the support of all sets of items (itemsets) and finding all of those that have a support above a minimum support threshold (large itemsets) ; 2) generating association rules using the large itemsets.

---
