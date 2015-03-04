from MoG_single_comp import MoG_SingleComponent
from util import jitchol

__author__ = 'AT'

from SAVIGP_full import SAVIGP_Full
import numpy as np

class SAVIGP_SingleComponent(SAVIGP_Full):
    def __init__(self, X, Y, num_inducing, num_MoG_comp, likelihood, kernels, n_samples, config_list):
        super(SAVIGP_Full, self).__init__(X, Y, num_inducing, num_MoG_comp, likelihood, kernels, n_samples, config_list)

    def _get_MoG(self):
        return MoG_SingleComponent(self.num_latent_proc, self.num_inducing)

    def _d_ent_d_m(self):
        return np.zeros((self.num_MoG_comp, self.num_latent_proc, self.num_inducing))

    def _d_ent_d_pi(self):
        return -self.log_z[0] - 1

    def _d_ent_d_S_kj(self, k, j):
        return self.MoG.invC_klj[0,0,j]

    def _d_ent_d_S(self):
        dent_ds = np.empty((self.num_MoG_comp, self.num_latent_proc) + self.MoG.S_dim())
        for k in range(self.num_MoG_comp):
            for j in range(self.num_latent_proc):
                dent_ds[k,j] = self._d_ent_d_S_kj(k,j)
        return dent_ds

    def _l_ent(self):
        return -np.dot(self.MoG.pi,  self.log_z)


    def update_N_z(self):
        self.log_z = np.zeros((self.num_MoG_comp))
        for j in range(self.num_latent_proc):
            self.log_z[0] += self.MoG.log_pdf(j, 0, 0)

    def _transformed_d_ent_d_S(self):
        return self.MoG.transform_eye_grad()