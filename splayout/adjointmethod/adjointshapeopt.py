from ..utils.utils import *
import numpy as np

class AdjointForShapeOpt:
    """
    Adjoint Method for Shape Derivative Optimization.

    Parameters
    ----------
    fdtd_engine : FDTDSimulation
        The FDTDSimulation object.
    fom_monitor_name : String
        Monitor name for deriving FoM.
    target_fom : Array
        Target FoM at different frequencies.
    design_region : ShapeOptRegion2D or ShapeOptRegion3D
        Design region for shape derivative method.
    forward_source_name : String
        Source name for Forward simulation.
    backward_source_name : String
        Source name for Adjoint simulation.
    dx : Float
        Micro element unit for gradient calculation(unit: μm, default: 0.001).
    sim_name : String
        New name for the components in Lumerical(default: "Adjoint").
    record_forward_field : Bool or Int
        Whether to record field in the forward simulation.
    """
    def __init__(self, fdtd_engine, fom_monitor_name, target_fom, design_region, forward_source_name, backward_source_name, dx = 0.001, sim_name = "Adjoint", record_forward_field = 1):
        self.fdtd_engine = fdtd_engine
        self.design_region = design_region
        self.fom_monitor_name = fom_monitor_name
        self.target_fom = target_fom
        self.forward_source_name = forward_source_name
        self.backward_source_name = backward_source_name
        self.dx = dx
        self.sim_name = sim_name
        self.record_forward_field = record_forward_field

    @staticmethod
    def cal_epsilon_diff_in_CAD(fdtd_engine, design_region, params, origin_epsilon_name, data_name, dx):
        """
        Calculate epsilon difference between new structure and original structure in Lumerical CAD.
        (From: lumopt. https://github.com/chriskeraly/lumopt)

        Parameters
        ----------
        fdtd_engine : FDTDSimulation
            The FDTDSimulation object.
        design_region : ShapeOptRegion2D or ShapeOptRegion3D
            Design region for shape derivative method.
        params : Array
            Parameters for the structure.
        origin_epsilon_name : String
            Name of the data in Lumerical FDTD that records the original epsilon distribution.
        data_name : String
            New name for the components in Lumerical(default: "Adjoint").
        dx : Float
            Micro element unit for gradient calculation(unit: μm).

        Returns
        -------
        data_name : String
            The name of the data in Lumerical.
        """
        fdtd_engine.switch_to_layout()
        fdtd_engine.eval("{0} = cell({1});".format(data_name, params.size))
        fdtd_engine.lumapi.putDouble(fdtd_engine.fdtd.handle, "dx", dx * 1e-6)
        fdtd_engine.fdtd.redrawoff()
        for i, param in enumerate(params):
            perturbed_params = params.copy()
            perturbed_params[i] = param + dx
            design_region.update(perturbed_params)
            pertrubed_epsilon_name = fdtd_engine.get_epsilon_distribution_in_CAD(index_monitor_name=design_region.index_region_name,
                                                                                 data_name="perturbed_epsilon")
            fdtd_engine.eval(
                "{0}".format(data_name) + "{" + str(i + 1) + "}" + "= ({0} - {1}) / dx;".format(pertrubed_epsilon_name,
                                                                                                origin_epsilon_name))
        fdtd_engine.eval("clear({0}, {1}, dx);".format(origin_epsilon_name, pertrubed_epsilon_name))
        fdtd_engine.fdtd.redrawon()
        return data_name

    @staticmethod
    def cal_partial_fom_in_CAD(fdtd_engine, forward_field_name, adjoint_field_name, scaling_factor_name, epsilon_diff_name):
        """
        Calculate Partial FoM in Lumerical CAD.
        (From: lumopt. https://github.com/chriskeraly/lumopt)

        Parameters
        ----------
        fdtd_engine : FDTDSimulation
            The FDTDSimulation object.
        forward_field_name : String
            Design region for shape derivative method.
        adjoint_field_name : String
            Parameters for the structure.
        scaling_factor_name : String
            Name of the data in Lumerical FDTD that records the original epsilon distribution.
        epsilon_diff_name : String
            New name for the components in Lumerical(default: "Adjoint").

        Returns
        -------
        partial_fom : Array
            Shape: (frequencies, number of parameters).
        """
        fdtd_engine.eval(
            "gradient_fields = 2.0 * eps0 * {0}.E * {1}.E;".format(forward_field_name, adjoint_field_name) +
            "num_opt_params = length({0});".format(epsilon_diff_name) +
            "num_wl_pts = length({0}.lambda);".format(forward_field_name) +
            "partial_fom_derivs_vs_lambda = matrix(num_wl_pts, num_opt_params);" +
            "for(param_idx = [1:num_opt_params]){" +
            "    for(wl_idx = [1:num_wl_pts]){" +
            "        spatial_integrand = pinch(sum(gradient_fields(:,:,:,wl_idx,:) * {0}(wl_idx)".format(
                scaling_factor_name) + " * {0}".format(epsilon_diff_name) + "{param_idx}, 5), 4); " +
            "        partial_fom_derivs_vs_lambda(wl_idx, param_idx) = integrate2(spatial_integrand, [1,2,3], {0}.x, {0}.y, {0}.z);".format(
                forward_field_name) +
            "    }" +
            "}")
        partial_fom = fdtd_engine.lumapi.getVar(fdtd_engine.fdtd.handle, 'partial_fom_derivs_vs_lambda')
        return partial_fom

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
        self.fdtd_engine.switch_to_layout()
        self.fdtd_engine.set_enable(self.forward_source_name)
        self.fdtd_engine.set_disable(self.backward_source_name)
        self.design_region.update(params)
        self.fdtd_engine.run()
        if (self.record_forward_field):
            self.forward_field = self.design_region.get_E_distribution()
        self.forward_field_name = self.design_region.get_E_distribution_in_CAD("ForwardField")
        self.forward_epsilon_name = self.design_region.get_epsilon_distribution_in_CAD("ForwardEpsilon")
        mode_coefficient = self.fdtd_engine.get_mode_coefficient(expansion_name=self.fom_monitor_name)
        forward_source_power = self.fdtd_engine.get_source_power(self.forward_source_name)
        self.T_fwd_vs_wavelength = np.real(mode_coefficient * mode_coefficient.conj() / forward_source_power)
        self.phase_prefactors = mode_coefficient / 4.0 / forward_source_power

        wavelength = self.fdtd_engine.get_wavelength()
        wavelength_range = wavelength.max() - wavelength.min()
        T_fwd_integrand = np.abs(self.target_fom) / wavelength_range
        const_term = np.trapz(y=T_fwd_integrand, x=wavelength)
        T_fwd_error = np.abs(self.T_fwd_vs_wavelength.flatten() - self.target_fom)
        T_fwd_error_integrand = T_fwd_error / wavelength_range
        error_term = np.trapz(y=T_fwd_error_integrand, x=wavelength)
        self.fom = const_term - error_term
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
        - T_fwd_partial_derivs / 1e6 : Array
            Gradients.
        """
        self.fdtd_engine.switch_to_layout()
        self.fdtd_engine.set_enable(self.backward_source_name)
        self.fdtd_engine.set_disable(self.forward_source_name)
        self.fdtd_engine.run()
        self.adjoint_field_name = self.design_region.get_E_distribution_in_CAD("BackwardField")

        omega = self.fdtd_engine.get_omega()
        adjoint_source_power = self.fdtd_engine.get_source_power(self.backward_source_name)
        scaling_factor = np.conj(self.phase_prefactors) * omega * 1j / np.sqrt(adjoint_source_power)

        epsilon_diff_name = self.cal_epsilon_diff_in_CAD(self.fdtd_engine, self.design_region, params,
                                                                      self.forward_epsilon_name, "epsilon_diff", self.dx)

        self.fdtd_engine.lumapi.putMatrix(self.fdtd_engine.fdtd.handle, "scaling_factor", scaling_factor)
        partial_fom = self.cal_partial_fom_in_CAD(self.fdtd_engine, self.forward_field_name, self.adjoint_field_name,
                                                        "scaling_factor", epsilon_diff_name)

        wavelength = self.fdtd_engine.get_wavelength()
        wavelength_range = wavelength.max() - wavelength.min()
        T_fwd_error = self.T_fwd_vs_wavelength - self.target_fom
        const_factor = -1.0
        integral_kernel = np.sign(T_fwd_error) / wavelength_range

        d = np.diff(wavelength)

        quad_weight = np.append(np.append(d[0], d[0:-1] + d[1:]), d[-1]) / 2
        v = const_factor * integral_kernel.flatten() * quad_weight
        T_fwd_partial_derivs = partial_fom.transpose().dot(v).flatten().real
        return - T_fwd_partial_derivs / 1e6

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