from ..utils.utils import *
from .topologyregion3d import TopologyOptRegion3D
from .topologyregion2d import TopologyOptRegion2D
from .scalabletoregion3d import ScalableToOptRegion3D
import numpy as np
import scipy.constants

class AdjointForTO:
    """
    Adjoint Method for Topology Optimization.

    Parameters
    ----------
    fdtd_engine : FDTDSimulation
        The FDTDSimulation object.
    T_monitor_names : String or List of String
        Monitor names for deriving FoM.
    target_T : Array or List of Array
        Target Transmissions at different frequencies.
    design_region : TopologyOptRegion2D or TopologyOptRegion3D or ScalableToOptRegion3D
        Design region for shape derivative method.
    forward_source_names : String or List of String
        Source names for Forward simulation.
    backward_source_names : String or List of String
        Source names for Adjoint simulation.
    sim_name : String
        Name of the temporary simulation(default: "Adjoint").
    y_antisymmetric : Bool or Int
        Whether set y-axis antisymmetric in the simulation(default: 0).
    if_default_fom : Bool or Int
        `Whether use the default figure of merit(default: 1).
    backward_T_monitor_names : String or List of String
        Monitor names for deriving FoM which need to calculate in the backward direction.
    """
    def __init__(self,fdtd_engine, T_monitor_names, target_T, design_region, forward_source_names, backward_source_names,
                 sim_name = "Adjoint", y_antisymmetric = 0, if_default_fom = 1, backward_T_monitor_names = None):
        self.fdtd_engine = fdtd_engine
        self.design_region = design_region
        self.T_monitor_names = np.array([T_monitor_names]).flatten()
        self.target_T = np.reshape(np.array([target_T]), (np.shape(self.T_monitor_names)[0], -1))
        self.forward_source_names = np.array([forward_source_names]).flatten()
        self.backward_source_names = np.array([backward_source_names]).flatten()
        self.sim_name = sim_name
        self.y_antisymmetric = y_antisymmetric
        self.multi_target_flag = 0
        self.if_default_fom = if_default_fom
        if backward_T_monitor_names is None:
            self.backward_T_monitor_names = []
        else:
            self.backward_T_monitor_names = np.array([backward_T_monitor_names]).flatten()

    def get_total_source_power(self, source_names):
        """
        Calculate the total power of sources.
        Parameters
        ----------
        forward_source_names : List of String
        Source names for simulation.

        Returns
        -------
        - total_source_power : Float
            The total power of sources.
        """
        total_source_power = self.fdtd_engine.get_source_power(source_names[0])
        for i in range(1, np.shape(source_names)[0]):
            total_source_power += self.fdtd_engine.get_source_power(source_names[i])
        return total_source_power

    def get_forward_transmission_properties(self):
        """
        Calculate transmission properties of the forward simulation.
        """
        mode_coefficients = []
        for i in range(0, np.shape(self.T_monitor_names)[0]):
            if self.T_monitor_names[i] in self.backward_T_monitor_names:
                mode_coefficients.append(
                    self.fdtd_engine.get_mode_coefficient(expansion_name=str(self.T_monitor_names[i]),
                                                          direction=BACKWARD))
            else:
                mode_coefficients.append(
                    self.fdtd_engine.get_mode_coefficient(expansion_name=str(self.T_monitor_names[i])))
        mode_coefficients = np.array(mode_coefficients)
        forward_source_power = self.get_total_source_power(self.forward_source_names)
        self.T_fwd_vs_wavelengths = np.real(mode_coefficients * mode_coefficients.conj() / forward_source_power)
        self.phase_prefactors = mode_coefficients / 4.0 / forward_source_power

    def call_fom(self, params):
        """
        Calculate FoM(Figure of Merit) and return.
        (Reference: lumopt. https://github.com/chriskeraly/lumopt)

        Parameters
        ----------
        params : Array
            Parameters for the structure.

        Returns
        -------
        - self.fom : Float
            Figure of Merit (if_default_fom = 1) or Transmission(if_default_fom = 0).
        """
        params = np.reshape(params,(self.design_region.get_x_size(),self.design_region.get_y_size()))
        self.fdtd_engine.switch_to_layout()
        self.fdtd_engine.set_enable(self.forward_source_names.tolist())
        self.fdtd_engine.set_disable(self.backward_source_names.tolist())
        self.design_region.update(params)
        self.fdtd_engine.run(self.sim_name)
        self.forward_field = self.design_region.get_E_distribution()

        self.get_forward_transmission_properties()

        if (self.if_default_fom == 1):
            wavelength = self.fdtd_engine.get_wavelength()
            wavelength_range = wavelength.max() - wavelength.min()
            if (wavelength.size > 1):
                T_fwd_integrand = np.abs(self.target_T) / wavelength_range
                const_term = np.trapz(y=T_fwd_integrand, x=wavelength, axis=1)
                T_fwd_error = np.abs(np.squeeze(self.T_fwd_vs_wavelengths) - self.target_T)
                T_fwd_error_integrand = T_fwd_error / wavelength_range
                error_term = np.trapz(y=T_fwd_error_integrand, x=wavelength, axis=1)
                self.fom = const_term - error_term
            else:
                self.fom = np.squeeze(np.abs(self.target_T) - np.abs(self.T_fwd_vs_wavelengths.flatten() - self.target_T),
                                      axis=1)
        else:
            self.fom = self.T_fwd_vs_wavelengths

        return self.fom

    def call_grad(self, params):
        """
        Calculate Gradient(Figure of Merit) and return.
        (Reference: lumopt. https://github.com/chriskeraly/lumopt)

        Parameters
        ----------
        params : Array
            Parameters for the structure.

        Returns
        -------
        - T_fwd_partial_derivs: Array
            Gradients.
        """
        self.fdtd_engine.switch_to_layout()
        self.fdtd_engine.set_disable(self.forward_source_names.tolist())
        self.fdtd_engine.set_disable(self.backward_source_names.tolist())
        omega = self.fdtd_engine.get_omega()
        wavelength = self.fdtd_engine.get_wavelength()
        wavelength_range = wavelength.max() - wavelength.min()

        d = np.diff(wavelength)
        T_fwd_partial_derivs = []
        for i in range(0, np.shape(self.backward_source_names)[0]):
            self.fdtd_engine.set_enable(self.backward_source_names[i])
            self.fdtd_engine.run()
            adjoint_source_power = self.fdtd_engine.get_source_power(self.backward_source_names[i])
            scaling_factor = np.conj(self.phase_prefactors[i]) * omega * 1j / np.sqrt(adjoint_source_power)
            if type(self.design_region) == TopologyOptRegion3D:
                self.adjoint_field, x_list, y_list, z_list = self.design_region.get_E_distribution(if_get_spatial=1)
                cell = self.design_region.x_mesh * 1e-6 * self.design_region.y_mesh * 1e-6 * self.design_region.z_mesh * 1e-6
                gradient_field = np.sum(
                    np.sum(2.0 * cell * scipy.constants.epsilon_0 * self.forward_field * self.adjoint_field, axis=4),
                    axis=2)
                dF_dEps = gradient_field
            elif type(self.design_region) == TopologyOptRegion2D:
                self.adjoint_field = self.design_region.get_E_distribution()
                gradient_field = 2.0 * self.design_region.x_mesh * 1e-6 * self.design_region.y_mesh * 1e-6 * scipy.constants.epsilon_0 * self.forward_field * self.adjoint_field
                dF_dEps = np.squeeze(np.sum(gradient_field, axis=-1), axis=2)
            elif type(self.design_region) == ScalableToOptRegion3D:
                self.adjoint_field, x_list, y_list, z_list = self.design_region.get_E_distribution(if_get_spatial=1)
                cell = self.design_region.x_mesh * 1e-6 * self.design_region.y_mesh * 1e-6 * self.design_region.z_mesh * 1e-6
                gradient_field = np.sum(
                    np.sum(2.0 * cell * scipy.constants.epsilon_0 * self.forward_field * self.adjoint_field, axis=4),
                    axis=2)
                dF_dEps = np.zeros((self.design_region.get_x_size(), self.design_region.get_y_size(), gradient_field.shape[2]), dtype=gradient_field.dtype)
                for k in range(0, gradient_field.shape[2]):
                    dF_dEps[:, :, k] = self.design_region.scaling(gradient_field[:, :, k])
            else:
                raise Exception("Unacceptable design region provided.")


            for wl in range(0, len(omega)):
                dF_dEps[:,:, wl] = dF_dEps[:,:, wl]*scaling_factor[wl]

            if (self.y_antisymmetric):
                dF_dEps = np.real(dF_dEps)[:, int(dF_dEps.shape[1]/2):, :]
            else:
                dF_dEps = np.real(dF_dEps)

            topo_grad = dF_dEps * (self.design_region.higher_epsilon - self.design_region.lower_epsilon)
            partial_fom = topo_grad.reshape(-1, topo_grad.shape[-1])
            self.fdtd_engine.switch_to_layout()
            self.fdtd_engine.set_disable(self.backward_source_names[i])

            if (self.if_default_fom == 1):
                if (wavelength.size > 1):
                    T_fwd_error = self.T_fwd_vs_wavelengths[i] - self.target_T[i]
                    T_fwd_error_integrand = np.abs(T_fwd_error) / wavelength_range
                    const_factor = -1.0 * np.trapz(y = T_fwd_error_integrand, x = wavelength)
                    integral_kernel = np.sign(T_fwd_error) / wavelength_range
                    quad_weight = np.append(np.append(d[0], d[0:-1] + d[1:]),
                                            d[-1]) / 2
                    v = const_factor * integral_kernel.flatten() * quad_weight

                    T_fwd_partial_derivs.append(np.real(partial_fom).dot(v).flatten().real)
                else:
                    T_fwd_partial_derivs.append((-1.0*np.sign(self.T_fwd_vs_wavelengths[i] - self.target_T[i]) * np.real(partial_fom))[:, 0].real)

            else:
                T_fwd_partial_derivs.append(np.real(partial_fom))



        if (self.if_default_fom == 1):
            T_fwd_partial_derivs = - np.array(T_fwd_partial_derivs).transpose((1, 0))
        else:
            T_fwd_partial_derivs = np.array(T_fwd_partial_derivs).transpose((1, 0, 2))

        return T_fwd_partial_derivs

    def reset_T_monitor_names(self, T_monitor_names):
        """
        Rest fom monitor for deriving FoM.

        Parameters
        ----------
        T_monitor_names : String or List of String
            Monitor names for deriving FoM.
        """
        self.T_monitor_names = np.array([T_monitor_names]).flatten()

    def reset_forward_source_names(self, forward_source_names):
        """
        Rest source for Forward simulation.

        Parameters
        ----------
        forward_source_names : String or List of String
            Source names for Forward simulation.
        """
        self.forward_source_names = np.array([forward_source_names]).flatten()

    def reset_backward_source_names(self, backward_source_names):
        """
        Rest source for Adjoint simulation.

        Parameters
        ----------
        backward_source_names : String or List of String
            Source names for Adjoint simulation.

        """
        self.backward_source_names = np.array([backward_source_names]).flatten()

    def reset_target_T(self, target_T):
        """
        Rest target FoMs at different frequencies.

        Parameters
        ----------
        target_T : Array or List of Array
            Target FoMs at different frequencies.
        """
        self.target_T = np.reshape(np.array([target_T]), (np.shape(self.T_monitor_names)[0], -1))