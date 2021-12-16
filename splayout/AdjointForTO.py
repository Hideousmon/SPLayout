from splayout.utils import *
from splayout.TopologyOptRegion3D import TopologyOptRegion3D
import numpy as np
import scipy.constants

class AdjointForTO:
    """
    Adjoint Method for Topology Optimization.

    Parameters
    ----------
    fdtd_engine : FDTDSimulation
        The FDTDSimulation object.
    fom_monitor_name : String or List of String
        Monitor names for deriving FoM.
    target_fom : Array or List of Array
        Target FoMs at different frequencies.
    design_region : TopologyOptRegion2D or TopologyOptRegion3D
        Design region for shape derivative method.
    forward_source_name : String or List of String
        Source names for Forward simulation.
    backward_source_name : String or List of String
        Source names for Adjoint simulation.
    y_antisymmetric : Bool or Int
        Whether set y-axis antisymmetric in the simulation(default: 0).
    """
    def __init__(self,fdtd_engine, fom_monitor_name, target_fom, design_region, forward_source_name, backward_source_name, sim_name = "Adjoint", y_antisymmetric = 0):
        self.fdtd_engine = fdtd_engine
        self.design_region = design_region
        self.fom_monitor_name = fom_monitor_name
        self.target_fom = target_fom
        self.forward_source_name = forward_source_name
        self.backward_source_name = backward_source_name
        self.sim_name = sim_name
        self.y_antisymmetric = y_antisymmetric
        self.multi_target_flag = 0
        if (type(fom_monitor_name) == list or type(target_fom) == list or type(forward_source_name) == list or type(backward_source_name) == list):
            if (len(fom_monitor_name) == len(target_fom) == len(forward_source_name) == len(backward_source_name)):
                self.multi_target_flag = 1
                self.multi_target_fom = []
            else:
                raise Exception("Format of parameters is not unified!")


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
            Figure of Merit (Lower, better).
        """
        params = np.reshape(params,(self.design_region.get_x_size(),self.design_region.get_y_size()))
        self.fdtd_engine.switch_to_layout()
        self.fdtd_engine.set_enable(self.forward_source_name)
        self.fdtd_engine.set_disable(self.backward_source_name)
        self.design_region.update(params)
        self.fdtd_engine.run(self.sim_name)
        self.forward_field = self.design_region.get_E_distribution()
        wavelength = self.fdtd_engine.get_wavelength()
        wavelength_range = wavelength.max() - wavelength.min()
        if (not self.multi_target_flag):
            mode_coefficient =  self.fdtd_engine.get_mode_coefficient(expansion_name=self.fom_monitor_name)
            forward_source_power = self.fdtd_engine.get_source_power(self.forward_source_name)
            self.T_fwd_vs_wavelength = np.real(mode_coefficient * mode_coefficient.conj() / forward_source_power)
            self.phase_prefactors = mode_coefficient / 4.0 / forward_source_power
            T_fwd_integrand = np.abs(self.target_fom) / wavelength_range
            const_term = np.trapz(y=T_fwd_integrand, x=wavelength)
            T_fwd_error = np.abs(self.T_fwd_vs_wavelength.flatten() - self.target_fom)
            T_fwd_error_integrand = T_fwd_error / wavelength_range
            error_term = np.trapz(y=T_fwd_error_integrand, x=wavelength)
            self.fom = const_term - error_term
        else:
            self.T_fwd_vs_wavelength = []
            self.phase_prefactors = []
            forward_source_power = 0
            self.multi_target_fom = []
            for i in range(0, len(self.forward_source_name)):
                forward_source_power += self.fdtd_engine.get_source_power(self.forward_source_name[i])
            for i in range(0, len(self.target_fom)):
                mode_coefficient = self.fdtd_engine.get_mode_coefficient(expansion_name=self.fom_monitor_name[i])
                self.T_fwd_vs_wavelength.append(np.real(mode_coefficient * mode_coefficient.conj() / forward_source_power))
                self.phase_prefactors.append(mode_coefficient / 4.0 / forward_source_power)
                T_fwd_integrand = np.abs(self.target_fom[i]) / wavelength_range
                const_term = np.trapz(y=T_fwd_integrand, x=wavelength)
                T_fwd_error = np.abs(self.T_fwd_vs_wavelength[-1].flatten() - self.target_fom[i])
                T_fwd_error_integrand = T_fwd_error / wavelength_range
                error_term = np.trapz(y=T_fwd_error_integrand, x=wavelength)
                self.multi_target_fom.append(const_term - error_term)
            self.fom = np.mean(self.multi_target_fom)

        return - self.fom

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
        - T_fwd_partial_derivs / 1e6 : Array
            Gradients.
        """
        params = np.reshape(params, (self.design_region.get_x_size(), self.design_region.get_y_size()))
        self.fdtd_engine.switch_to_layout()
        self.fdtd_engine.set_disable(self.forward_source_name)
        if (not self.multi_target_flag):
            self.fdtd_engine.set_enable(self.backward_source_name)
            self.fdtd_engine.run(self.sim_name)

            omega = self.fdtd_engine.get_omega()
            adjoint_source_power = self.fdtd_engine.get_source_power(self.backward_source_name)
            scaling_factor = np.conj(self.phase_prefactors) * omega * 1j / np.sqrt(adjoint_source_power)

            if (type(self.design_region) == TopologyOptRegion3D):
                self.adjoint_field, x_list, y_list, z_list = self.design_region.get_E_distribution(if_get_spatial=1)
                # gradient_field = 2.0 * self.design_region.x_mesh * 1e-6 * self.design_region.y_mesh * 1e-6 * scipy.constants.epsilon_0 *\
                #                  scipy.integrate.simps(self.forward_field * self.adjoint_field,z_list, axis=2)*1e6
                cell = self.design_region.x_mesh * 1e-6 * self.design_region.y_mesh * 1e-6 * self.design_region.z_mesh * 1e-6
                gradient_field =np.sum( np.sum(2.0 *cell * scipy.constants.epsilon_0 *self.forward_field * self.adjoint_field, axis=4), axis=2 )
                # gradient_field =np.mean( np.sum(2.0 *cell * scipy.constants.epsilon_0 *self.forward_field * self.adjoint_field, axis=4), axis=2 )
                dF_dEps = gradient_field
            else:
                self.adjoint_field = self.design_region.get_E_distribution()
                gradient_field = 2.0 * self.design_region.x_mesh*1e-6 * self.design_region.y_mesh*1e-6 * scipy.constants.epsilon_0 *self.forward_field * self.adjoint_field
                dF_dEps = np.squeeze(np.sum(gradient_field, axis=-1), axis=2)


            for wl in range(0, len(omega)):
                dF_dEps[:,:, wl] = dF_dEps[:,:, wl]*scaling_factor[wl]

            if (self.y_antisymmetric):
                dF_dEps = np.real(dF_dEps)[:, int(dF_dEps.shape[1]/2):, :]
            else:
                dF_dEps = np.real(dF_dEps)
            rho = params
            print("dF_dEps:", dF_dEps)
            self.fdtd_engine.fdtd.putv("topo_rho", rho)
            self.fdtd_engine.fdtd.putv("dF_dEps", dF_dEps)
            self.fdtd_engine.fdtd.eval(('params = struct;'
                           'params.eps_levels=[{0},{1}];'
                           'params.filter_radius = {2};'
                           'params.beta = {3};'
                           'params.eta = {4};'
                           'params.dx = {5};'
                           'params.dy = {6};'
                           'params.dz = 0.0;'
                           'topo_grad = topoparamstogradient(params,topo_rho,dF_dEps);').format(self.design_region.lower_epsilon, self.design_region.higher_epsilon,
             self.design_region.filter_R * 1e-6, self.design_region.beta, self.design_region.eta,
             self.design_region.x_mesh * 1e-6, self.design_region.y_mesh * 1e-6))


            topo_grad = self.fdtd_engine.fdtd.getv("topo_grad")
            print("topo_grad:", topo_grad)
            partial_fom = topo_grad.reshape(-1, topo_grad.shape[-1])
            wavelength = self.fdtd_engine.get_wavelength()
            wavelength_range = wavelength.max() - wavelength.min()
            T_fwd_error = self.T_fwd_vs_wavelength - self.target_fom
            const_factor = -1.0
            integral_kernel = np.sign(T_fwd_error) / wavelength_range
            d = np.diff(wavelength)
            quad_weight = np.append(np.append(d[0], d[0:-1] + d[1:]),
                                    d[-1]) / 2  # < There is probably a more elegant way to do this
            v = const_factor * integral_kernel.flatten() * quad_weight
            T_fwd_partial_derivs = partial_fom.dot(v).flatten().real
        else:
            self.grad_list = []
            for i in range(0, len(self.target_fom)):
                self.fdtd_engine.switch_to_layout()
                self.fdtd_engine.set_disable(self.backward_source_name)
                self.fdtd_engine.set_enable(self.backward_source_name[i])
                self.fdtd_engine.run(self.sim_name)
                self.adjoint_field = self.design_region.get_E_distribution()
                omega = self.fdtd_engine.get_omega()
                adjoint_source_power = self.fdtd_engine.get_source_power(self.backward_source_name[i])
                scaling_factor = np.conj(self.phase_prefactors[i]) * omega * 1j / np.sqrt(adjoint_source_power)
                gradient_field = 2.0 * self.design_region.x_mesh * 1e-6 * self.design_region.y_mesh * 1e-6 * scipy.constants.epsilon_0 * self.forward_field * self.adjoint_field
                dF_dEps = np.squeeze(np.sum(gradient_field, axis=-1), axis=2)

                for wl in range(0, len(omega)):
                    dF_dEps[:, :, wl] = dF_dEps[:, :, wl] * scaling_factor[wl]

                if (self.y_antisymmetric):
                    dF_dEps = np.real(dF_dEps)[:, int(dF_dEps.shape[1] / 2):, :]
                else:
                    dF_dEps = np.real(dF_dEps)
                rho = params
                self.fdtd_engine.fdtd.putv("topo_rho", rho)
                self.fdtd_engine.fdtd.putv("dF_dEps", dF_dEps)
                self.fdtd_engine.fdtd.eval(('params = struct;'
                                            'params.eps_levels=[{0},{1}];'
                                            'params.filter_radius = {2};'
                                            'params.beta = {3};'
                                            'params.eta = {4};'
                                            'params.dx = {5};'
                                            'params.dy = {6};'
                                            'params.dz = 0.0;'
                                            'topo_grad = topoparamstogradient(params,topo_rho,dF_dEps);').format(
                    self.design_region.lower_epsilon, self.design_region.higher_epsilon,
                    self.design_region.filter_R * 1e-6, self.design_region.beta, self.design_region.eta,
                    self.design_region.x_mesh * 1e-6, self.design_region.y_mesh * 1e-6))
                topo_grad = self.fdtd_engine.fdtd.getv("topo_grad")
                partial_fom = topo_grad.reshape(-1, topo_grad.shape[-1])
                wavelength = self.fdtd_engine.get_wavelength()
                wavelength_range = wavelength.max() - wavelength.min()
                T_fwd_error = self.T_fwd_vs_wavelength[i] - self.target_fom[i]
                const_factor = -1.0
                integral_kernel = np.sign(T_fwd_error) / wavelength_range
                d = np.diff(wavelength)
                quad_weight = np.append(np.append(d[0], d[0:-1] + d[1:]),
                                        d[-1]) / 2  # < There is probably a more elegant way to do this
                v = const_factor * integral_kernel.flatten() * quad_weight
                T_fwd_partial_derivs = partial_fom.dot(v).flatten().real
                self.grad_list.append(T_fwd_partial_derivs)
            T_fwd_partial_derivs = np.sum(np.array(self.grad_list), axis=0)

        return - T_fwd_partial_derivs