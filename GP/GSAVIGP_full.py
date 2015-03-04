from MoG_Diag import MoG_Diag
from SAVIGP import SAVIGP
from SAVIGP_full import SAVIGP_Full
from util import cross_ent_normal
import numpy as np


class GSAVIGP_Full(SAVIGP_Full):
    """
    Scalable Variational Inference Gaussian Process where the conditional likelihood is gaussian

    :param X: input observations
    :param Y: outputs
    :param num_inducing: number of inducing variables
    :param num_MoG_comp: number of components of the MoG
    :param num_latent_proc: number of latent processes
    :param likelihood: conditional likelihood function
    :param normal_sigma: covariance matrix of the conditional likelihood function
    :param kernel: of the GP
    :param n_samples: number of samples drawn for approximating ell and its gradient
    :rtype: model object
    """
    def __init__(self, X, Y, num_inducing, num_MoG_comp, likelihood, normal_sigma, kernels, n_samples, config_list):
        self.normal_sigma = normal_sigma
        super(GSAVIGP_Full, self).__init__(X, Y, num_inducing, num_MoG_comp, likelihood, kernels, n_samples, config_list)

    def _ell(self, n_sample, p_X, p_Y, cond_log_likelihood):
        xell, xdell_dm, xdell_dS, xdell_dpi, xell_hyper = super(GSAVIGP_Full, self)._ell(n_sample, p_X, p_Y, cond_log_likelihood)
        gell = self._gaussian_ell(p_X, p_Y, self.normal_sigma)
        return gell, xdell_dm, xdell_dS, xdell_dpi, xell_hyper

    def _predict(self, Xnew, which_parts='all', full_cov=False, stop=False):
        return self._gaussian_predict(Xnew, self.normal_sigma)
