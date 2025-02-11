import numpy as np

from pyproximal.ProxOperator import _check_tau
from pyproximal import ProxOperator


class Log(ProxOperator):
    r"""Logarithmic penalty.

    The logarithmic penalty (Log) is defined as

    .. math::

        \mathrm{Log}_{\sigma,\gamma}(\mathbf{x}) = \sum_i \frac{\sigma}{\log(\gamma + 1)}\log(\gamma|x_i| + 1)

    where :math:`{\sigma>0}`, :math:`{\gamma>0}`.

    Parameters
    ----------
    sigma : :obj:`float`
        Regularization parameter.
    gamma : :obj:`float`, optional
        Regularization parameter. Default is 1.3.

    Notes
    -----
    The logarithmic penalty is an extension of the elastic net family of penalties to
    non-convex members, which should produce sparser solutions compared to the
    :math:`\ell_1`-penalty [1]_. The pyproximal implementation considers a scaled
    version that satisfies :math:`{\mathrm{Log}_{\sigma,\gamma}(0) = 0}` and
    :math:`{\mathrm{Log}_{\sigma,\gamma}(1) = \sigma}`, which is suitable also for
    penalizing singular values. Note that when :math:`{\gamma\rightarrow 0}` the
    logarithmic penalty approaches the l1-penalty and when
    :math:`{\gamma\rightarrow\infty}` it mimicks the :math:`\ell_0`-penalty.

    The proximal operator can be analyzed using the one-dimensional case

    .. math::
        \prox_{\tau \mathrm{Log}(\cdot)}(x) = \argmin_{z} \mathrm{Log}(z) + \frac{1}{2\tau}(x - z)^2

    where we assume that :math:`x\geq 0`. The minima can be obtained when :math:`z=0`
    or at a local minimum. Consider therefore

    .. math::
        f(z) = k \log(\gamma x + 1) + \frac{1}{2} (x - z)^2

    where :math:`k= \frac{\tau \sigma}{\log(\gamma + 1)}` is introduced for
    convenience. The condition that :math:`f'(z) = 0` yields the following equation

    .. math::
        \gamma z^2 + (1-\gamma y) x + k\gamma - y = 0 .

    The discriminant :math:`\Delta` is given by

    .. math::
        \Delta = (1-\gamma y)^2-4\gamma (k\gamma - y) .

    When the discriminant is negative the global optimum is obtained at
    :math:`z=0`; otherwise, it is obtained when

    .. math::
        z = \frac{\gamma x - 1 +\sqrt{\Delta}}{2\gamma} .

    Note that the other stationary point must be a local maximum since
    :math:`\gamma>0` and can therefore be discarded.

    .. [1] Friedman, J. H. "Fast sparse regression and classification",
        International Journal of Forecasting, 28(3):722 – 738, 2012.

    """

    def __init__(self, sigma, gamma=1.3):
        super().__init__(None, False)
        if sigma < 0:
            raise ValueError('Variable "sigma" must be positive.')
        if gamma < 0:
            raise ValueError('Variable "gamma" must be positive.')
        self.sigma = sigma
        self.gamma = gamma

    def __call__(self, x):
        return np.sum(self.elementwise(x))

    def elementwise(self, x):
        return self.sigma / np.log(self.gamma + 1) * np.log(self.gamma * np.abs(x) + 1)

    @_check_tau
    def prox(self, x, tau):
        k = tau * self.sigma / np.log(self.gamma + 1)
        out = np.zeros_like(x)
        b = self.gamma * np.abs(x) - 1
        discriminant = b ** 2 - 4 * self.gamma * (k * self.gamma - np.abs(x))
        idx = discriminant >= 0
        c = np.sqrt(discriminant[idx])
        # The stationary point (b[idx] - c) / (2 * self.gamma) is always a local maximum, and is therefore not checked
        r = np.vstack((np.zeros_like(c), (b[idx] + c) / (2 * self.gamma)))
        val = tau * self.elementwise(r) + (r - np.abs(x[idx])) ** 2 / 2
        idx_minima = np.argmin(val, axis=0)
        out[idx] = r[idx_minima, range(r.shape[1])]
        out *= np.sign(x)
        return out
