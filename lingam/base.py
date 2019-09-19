"""
Python implementation of the LiNGAM algorithms.
The LiNGAM Project: https://sites.google.com/site/sshimizu06/lingam
"""

from abc import ABCMeta, abstractmethod

import numpy as np
from sklearn.linear_model import LassoLarsIC, LinearRegression

from .bootstrap import BootstrapMixin


class _BaseLiNGAM(BootstrapMixin, metaclass=ABCMeta):
    """Base class for all LiNGAM algorithms."""

    def __init__(self, random_state=None):
        """Construct a _BaseLiNGAM model.

        Parameters
        ----------
        random_state : int, optional (default=None)
            random_state is the seed used by the random number generator.
        """
        self._random_state = random_state
        self._causal_order = None
        self._adjacency_matrix = None

    @abstractmethod
    def fit(self, X):
        """Subclasses should implement this method!
        Fit the model to X.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data, where n_samples is the number of samples
            and n_features is the number of features.

        Returns
        -------
        self : object
            Returns the instance itself.
        """

    def _estimate_adjacency_matrix(self, X):
        """Estimate adjacency matrix by causal order.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_features)
            Training data, where n_samples is the number of samples
            and n_features is the number of features.

        Returns
        -------
        self : object
            Returns the instance itself.
        """
        gamma = 1.0

        B = np.zeros([X.shape[1], X.shape[1]], dtype='float64')
        for i in range(1, len(self._causal_order)):
            lr = LinearRegression()
            lr.fit(X[:, self._causal_order[:i]], X[:, self._causal_order[i]])
            weight = np.power(np.abs(lr.coef_), gamma)

            reg = LassoLarsIC(criterion='bic')
            reg.fit(X[:, self._causal_order[:i]] * weight,
                    X[:, self._causal_order[i]])

            B[self._causal_order[i], self._causal_order[:i]] = reg.coef_ * weight

        self._adjacency_matrix = B
        return self

    @property
    def causal_order_(self):
        """Estimated causal ordering.

        Returns
        -------
        causal_order_ : array-like, shape (n_features)
            The causal order of fitted model, where 
            n_features is the number of features.
        """
        return self._causal_order

    @property
    def adjacency_matrix_(self):
        """Estimated adjacency matrix.

        Returns
        -------
        adjacency_matrix_ : array-like, shape (n_features, n_features)
            The adjacency matrix B of fitted model, where 
            n_features is the number of features.
        """
        return self._adjacency_matrix