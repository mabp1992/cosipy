# import numpy as np
# from astropy.coordinates import Angle, SkyCoord
# import astropy.units as u
# import matplotlib.pyplot as plt
# from scipy.optimize import curve_fit
# from cosipy.polarization.polarization_angle import PolarizationAngle
# from cosipy.polarization.conventions import MEGAlibRelativeX, MEGAlibRelativeY, MEGAlibRelativeZ, IAUPolarizationConvention
# from cosipy.response import FullDetectorResponse
# from scoords import SpacecraftFrame
# from threeML import LinearPolarization
# import scipy.interpolate as interpolate
# from histpy import Histogram

# import logging
# logger = logging.getLogger(__name__)

# #we can define all these functions in a separate file to import

# def R(x, A, B, C):
#     """ Function to fit to the modulation of the azimuthal angle distribution.
#     """
#     return A + B*(np.cos(x + C)**2)

# def constant(x, a):
#         """
#         Constant function to fit to mu_100 values.

#         Parameters
#         ----------
#         x : float
#             Mu_100
#         a : float
#             Parameter

#         Returns
#         -------
#         a : float
#             Constant value
#         """

#         return a

# def stokes_u(phi):
#     """
#     Calculate the U Stokes parameter from the azimuthal angle phi.

#     Parameters
#     ----------
#     phi : float
#         Azimuthal angle in radians

#     Returns
#     -------
#     u : float
#         U Stokes parameter
#     """
#     return np.sin(phi * 2) * 2

# def stokes_q(phi):
#     """
#         Calculate the Q Stokes parameter from the azimuthal angle phi.

#         Parameters
#         ----------
#         phi : float
#             Azimuthal angle in radians

#         Returns
#         -------
#         q : float
#             Q Stokes parameter
#         """
#     return np.cos(phi * 2) * 2

# def rotate_points_to_x_axis(newPD, newPA):
#     """
#     Rotate arrays of points (x_, y_) in the QN-UN plane by an angle

#     Parameters
#     ----------
#     newPD : float
#         Polarization degree
#     newPA : float
#         Polarization angle
#     Returns
#     -------
#     rotated_Q : float
#         Q Stokes parameter
#     rotated_U : float
#         U Stokes parameter

#     """
#     # Create a matrix of rotation matrices for each point
#     rotated_Q = newPD * np.cos(2 * newPA)
#     rotated_U = newPD * np.sin(2 * newPA)

#     return rotated_Q, rotated_U

# def polar_chart_backbone(ax):
#     """ Preparing canvas for Stokes chart
#     Parameters
#     ----------
#     ax : matplotlib.axes._axes.Axes
#         Axes to plot on
#     """
#     ax.spines['top'].set_visible(True)
#     ax.spines['right'].set_visible(True)
#     c0 = plt.Circle((0,0), radius=0.25, facecolor='none', edgecolor='k', linewidth=1, linestyle='--', alpha=0.3)
#     c1 = plt.Circle((0,0), radius=0.50, facecolor='none', edgecolor='k', linewidth=1, linestyle='--', alpha=0.3)
#     c2 = plt.Circle((0,0), radius=0.75, facecolor='none', edgecolor='k', linewidth=1, linestyle='--', alpha=0.3)
#     c3 = plt.Circle((0,0), radius=1.00, facecolor='none', edgecolor='k', linewidth=1, linestyle='-', alpha=0.5)
#     plt.gca().add_artist(c0)
#     plt.gca().add_artist(c1)
#     plt.gca().add_artist(c2)
#     plt.gca().add_artist(c3)
#     plt.annotate('0.25', (0.25, 0), textcoords="offset points", xytext=(10,0), ha='center', fontsize=8, color='k', alpha=0.3)
#     plt.annotate('0.50', (0.50, 0), textcoords="offset points", xytext=(10,0), ha='center', fontsize=8, color='k', alpha=0.3)
#     plt.annotate('0.75', (0.75, 0), textcoords="offset points", xytext=(10,0), ha='center', fontsize=8, color='k', alpha=0.3)
#     plt.annotate('1.00', (1.00, 0), textcoords="offset points", xytext=(10,0), ha='center', fontsize=8, color='k', alpha=0.3)
#     plt.hlines(0, -1, 1, linewidth=1, color='k', linestyle='--', alpha=0.3)
#     plt.vlines(0, -1, 1, linewidth=1, color='k', linestyle='--', alpha=0.3)
#     plt.plot([1,-1], [1,-1], linewidth=1, color='k', linestyle='--', alpha=0.3)
#     plt.plot([1,-1], [-1,1], linewidth=1, color='k', linestyle='--', alpha=0.3)

# def calculate_azimuthal_scattering_angle(psi, chi, source_vector, reference_vector):
#         """
#         Calculate the azimuthal scattering angle of a scattered photon.

#         Parameters
#         ----------
#         psi : float
#             Polar angle (radians) of scattered photon in local coordinates
#         chi : float
#             Azimuthal angle (radians) of scattered photon in local coordinates
#         source_vector : astropy.coordinates.SkyCoord
#             Source direction
#         reference_vector : astropy.coordinates.SkyCoord
#             Reference direction (e.g. X-axis of spacecraft frame)

#         Returns
#         -------
#         azimuthal_angle : astropy.coordinates.Angle
#             Azimuthal scattering angle defined with respect to given reference vector
#         """

#         source_vector_cartesian = [source_vector.cartesian.x.value,
#                                    source_vector.cartesian.y.value,
#                                    source_vector.cartesian.z.value]
#         reference_vector_cartesian = [reference_vector.cartesian.x.value,
#                                       reference_vector.cartesian.y.value,
#                                       reference_vector.cartesian.z.value]

#         # Convert scattered photon vector from spherical to Cartesian coordinates
#         scattered_photon_vector = [np.sin(psi) * np.cos(chi), np.sin(psi) * np.sin(chi), np.cos(psi)]

#         # Project scattered photon vector onto plane perpendicular to source direction
#         d = np.dot(scattered_photon_vector, source_vector_cartesian) / np.dot(source_vector_cartesian, source_vector_cartesian)
#         projection = [scattered_photon_vector[0] - (d * source_vector_cartesian[0]),
#                       scattered_photon_vector[1] - (d * source_vector_cartesian[1]),
#                       scattered_photon_vector[2] - (d * source_vector_cartesian[2])]

#         # Calculate angle between scattered photon vector & reference vector on plane perpendicular to source direction
#         cross_product = np.cross(projection, reference_vector_cartesian)
#         if np.dot(source_vector_cartesian, cross_product) < 0:
#             sign = -1
#         else:
#             sign = 1
#         normalization = np.sqrt(np.dot(projection, projection)) * np.sqrt(np.dot(reference_vector_cartesian, reference_vector_cartesian))

#         azimuthal_angle = Angle(sign * np.arccos(np.dot(projection, reference_vector_cartesian) / normalization), unit=u.rad)

#         return azimuthal_angle

# def get_modulation(_x, _y, title='Modulation', show=False):
#     """ Function to estimate the modulation factor.
#         _x is the central value of the histogram bins
#         _y is the value of the bins on the histograms

#         Parameters
#         ----------
#         _x : array
#             Central values of the histogram bins
#         _y : array
#             Values of the histogram bins
#         title : str
#             Title of the plot
#         show : bool
#             Whether to show the plot or not

#         Returns
#         -------
#         mu : float
#             Modulation factor
#         mu_err : float
#             Error on the modulation factor
#     """

#     popt, pcov = curve_fit(R, _x, _y ) #sigma=np.sqrt(_y), absolute_sigma=True
#     pcov[0][0], pcov[1][1], pcov[2][2] = np.sqrt(pcov[0][0]), np.sqrt(pcov[1][1]), np.sqrt(pcov[2][2])
#     print('A = %.2f, B = %.2f, C = %.2f'%(popt[0], popt[1], popt[2]))

#     Rmax, Rmin = np.amax(R(_x, *popt)), np.amin(R(_x, *popt))
#     print('Rmax, Rmin:', Rmax, Rmin)
#     mu = (Rmax-Rmin)/(Rmax+Rmin)
#     print('Modulation mu = ', mu)

#     mu_err = 2/(popt[1]+2*popt[0])**2 * np.sqrt(popt[1]**2 * pcov[0][0]**2 + popt[0]**2 * pcov[1][1]**2)

#     if show:

#         plt.figure()
#         plt.title(title)
#         plt.step(_x, _y, where='mid')
#         perr = [popt[0]+np.sqrt(pcov[0][0]), popt[1]+np.sqrt(pcov[1][1]), popt[2]]
#         merr = [popt[0]-np.sqrt(pcov[0][0]), popt[1]-np.sqrt(pcov[1][1]), popt[2]]
#         plt.fill_between(_x, R(_x, *perr), R(_x, *merr), color='red', alpha=0.3)
#         plt.plot(_x, R(_x, *popt), 'r-', label=r'$\mu=$%.3f'%(mu))
#         plt.legend(fontsize=12)
#         plt.xlabel('Azimuthal angle [rad]')
#         plt.savefig('%s'%title)

#     return mu, mu_err

# def create_asad_from_response(spectrum, polarization_level, polarization_angle, source_vector, ori, response,
#                               convention, response_file, response_convention, bins=20):
#     """
#     Convolve source spectrum with response and calculate azimuthal scattering angle bins.

#     Parameters
#     ----------
#     spectrum : :py:class:`threeML.Model`
#         Spectral model.
#     polarization_level : float
#         Polarization level (between 0 and 1).
#     polarization_angle : :py:class:`cosipy.polarization.polarization_angle.PolarizationAngle`
#         Polarization angle. If in the spacecraft frame, the angle must have the same convention as the response.
#     bins : int or astropy.units.quantity.Quantity, optional
#         Number of azimuthal scattering angle bins if int or array of edges of azimuthal scattering angle bins if Quantity
#     source_vector : astropy.coordinates.sky_coordinate.SkyCoord
#         Source direction
#     ori : cosipy.spacecraftfile.SpacecraftFile.SpacecraftFile
#         Spacecraft orientation
#     response : cosipy.response.FullDetectorResponse.FullDetectorResponse
#         Response object
#     convention : cosipy.polarization.PolarizationConvention
#         Polarization convention
#     response_file : str or pathlib.Path
#         Path to detector response
#     response_convention : str
#         Response convention. If in the spacecraft frame, the angle must have the same convention as the response.

#     Returns
#     -------
#     asad : histpy.Histogram
#         Counts in each azimuthal scattering angle bin
#     """

#     if isinstance(convention.frame, SpacecraftFrame):

#         target_in_sc_frame = ori.get_target_in_sc_frame(target_name='source', target_coord=source_vector.transform_to('galactic'))
#         dwell_time_map = ori.get_dwell_map(response=response_file, src_path=target_in_sc_frame, pa_convention=response_convention)
#         psr = response.get_point_source_response(exposure_map=dwell_time_map, coord=source_vector.transform_to('galactic'))
#         expectation = psr.get_expectation(spectrum, LinearPolarization(polarization_level * 100., polarization_angle.angle.deg))

#         azimuthal_angle_bins = []

#         for i in range(expectation.axes['PsiChi'].nbins):
#             psichi = SkyCoord(lat=(np.pi/2) - expectation.axes['PsiChi'].pix2ang(i)[0], lon=expectation.axes['PsiChi'].pix2ang(i)[1], unit=u.rad, frame=convention.frame)
#             azimuthal_angle = PolarizationAngle.from_scattering_direction(psichi, source_vector, convention)
#             azimuthal_angle_bins.append(azimuthal_angle.angle)

#     else:

#         scatt_map = ori.get_scatt_map(nside=response.nside*2, target_coord=source_vector)
#         # scatt_map = ori.get_scatt_map(nside=response.nside*2, target_coord=source_vector, coordsys='galactic')
#         psr = response.get_point_source_response(coord=source_vector, scatt_map=scatt_map)
#         expectation = psr.get_expectation(spectrum, LinearPolarization(polarization_level * 100., polarization_angle.angle.deg))

#         azimuthal_angle_bins = []

#         for i in range(expectation.axes['PsiChi'].nbins):
#             psichi = expectation.axes['PsiChi'].pix2skycoord(i).transform_to('icrs')
#             azimuthal_angle = PolarizationAngle.from_scattering_direction(psichi, source_vector, convention)
#             azimuthal_angle_bins.append(azimuthal_angle.angle)

#     if isinstance(bins, int):
#         bin_edges = Angle(np.linspace(-np.pi, np.pi, bins), unit=u.rad)
#     else:
#         bin_edges = bins

#     asad = []

#     for i in range(len(bin_edges)-1):
#         counts = 0
#         for j in range(expectation.project(['PsiChi']).nbins):
#             if azimuthal_angle_bins[j] >= bin_edges[i] and azimuthal_angle_bins[j] < bin_edges[i+1]:
#                 counts += expectation.project(['PsiChi'])[j]
#         asad.append(counts)

#     asad = Histogram(bin_edges, contents=asad)

#     return asad

# def create_unpolarized_asad(spectrum, source_vector, ori, response, convention, response_file, response_convention, bins=20):
#         """
#         Create unpolarized ASAD from response.

#         Parameters
#         ----------
#         bins : int or astropy.units.quantity.Quantity, optional
#             Number of azimuthal scattering angle bins if int or array of edges of azimuthal scattering angle bins if Quantity
#         spectrum : :py:class:`threeML.Model`
#             Spectral model.
#         source_vector : astropy.coordinates.sky_coordinate.SkyCoord
#             Source direction:
#         ori : cosipy.spacecraftfile.SpacecraftFile.SpacecraftFile
#             Spacecraft orientation
#         response : cosipy.response.FullDetectorResponse.FullDetectorResponse
#             Response object
#         convention : cosipy.polarization.PolarizationConvention
#             Polarization convention
#         response_file : str or pathlib.Path
#             Path to detector response
#         response_convention : str
#             Response convention. If in the spacecraft frame, the angle must have the same convention as the response.
#         Returns
#         -------
#         asad : histpy.Histogram
#             Counts in each azimuthal scattering angle bin
#         """
#         pd = 0
#         pa = PolarizationAngle(Angle(0 * u.deg), source_vector, convention=convention)
#         unpolarized_asad = create_asad_from_response(spectrum, pd, pa, source_vector, ori,
#                                                      response, convention, response_file,
#                                                      response_convention, bins=bins)

#         return unpolarized_asad

# def create_polarized_asads(spectrum, source_vector, ori, response, convention, response_file, response_convention, bins=20):
#         """
#         Create 100% polarized ASADs for each polarization angle bin of response.

#         Parameters
#         ----------
#         bins : int or astropy.units.quantity.Quantity, optional
#             Number of azimuthal scattering angle bins if int or array of edges of azimuthal scattering angle bins if Quantity

#         Returns
#         -------
#         polarized_asads : dict of histpy.Histogram
#             Counts in each azimuthal scattering angle bin for each polarization angle bin
#         """

#         polarized_asads = {}
#         for k in range(response.axes['Pol'].nbins):
#             pd = 1
#             pa = PolarizationAngle(Angle(response.axes['Pol'].centers.angle.to_value(u.deg)[k] * u.deg), source_vector, convention=convention)
#             polarized_asads[k] = create_asad_from_response(spectrum, pd, pa, source_vector, ori,
#                                                             response, convention, response_file,
#                                                             response_convention, bins=bins)
#         return polarized_asads

# class PolarizationStokes():
#     """
#     Stokes parameter method to fit polarization.

#     Parameters
#     ----------
#     source_vector : astropy.coordinates.sky_coordinate.SkyCoord
#         Source direction
#     source_spectrum : astromodels.functions.functions_1D
#         Spectrum of source

#     data : list of dict
#         Data to fit
#     background : list of dict
#         Background to fit
#     response_convention : str
#         Response convention
#     response_file : str or pathlib.Path
#         Path to detector response
#     sc_orientation : cosipy.spacecraftfile.SpacecraftFile.SpacecraftFile
#         Spacecraft orientation
#     fit_convention : cosipy.polarization.PolarizationConvention
#         Polarization convention for the fit
#     show_plots : bool
#         Whether to show plots or not
#     """


#     def __init__(self, source_vector, source_spectrum, data,
#                  response_file, sc_orientation, background=None, response_convention='RelativeX',
#                  fit_convention=IAUPolarizationConvention(), asad_bin_edges=None, show_plots=False):

#         ###################### This will need to be changed into IAUPolarizationConvention hardcoded!
#         ######################
#         print('This class loading takes around 30 seconds... \n')
#         ######################

#         if isinstance(fit_convention.frame, SpacecraftFrame) and not isinstance(source_vector.frame, SpacecraftFrame):
#             attitude = sc_orientation.get_attitude()[0]
#             source_vector = source_vector.transform_to(SpacecraftFrame(attitude=attitude))
#             logger.warning('The source direction is being converted to the spacecraft frame using the attitude at the first timestamp of the orientation.')
#         elif not isinstance(fit_convention.frame, SpacecraftFrame):
#             source_vector = source_vector.transform_to('icrs')

#         if ((isinstance(fit_convention, MEGAlibRelativeX) and response_convention != 'RelativeX') or
#             (isinstance(fit_convention, MEGAlibRelativeY) and response_convention != 'RelativeY') or
#             (isinstance(fit_convention, MEGAlibRelativeZ) and response_convention != 'RelativeZ')):
#             raise RuntimeError("If performing fit in spacecraft frame, fit convention must match convention of response.")

#         # if not type(data) == list:
#         #     self._data = [data]
#         # else:
#         #     self._data = data

#         self.SHOW_PLOTS = show_plots

#         self._ori = sc_orientation

#         self._convention = fit_convention

#         self._response_convention = response_convention

#         self._response_file = response_file

#         self._response = FullDetectorResponse.open(response_file, pa_convention=self._response_convention)

#         self._source_vector = source_vector

#         self._spectrum = source_spectrum

#         self._nbins = self._response.axes['Pol'].nbins
#         print('Number of azimuthal angle bins used:', self._nbins)

#         self.asad_bin_edges = asad_bin_edges

#         # self._binedges = Angle(np.linspace(-np.pi, np.pi, self._nbins), unit=u.rad)

#         self._reference_vector = self._convention.get_basis(source_vector)[0]

#         self._expectation, self._azimuthal_angle_bins = self.convolve_spectrum(source_spectrum)

#         self._energy_range = [min(self._response.axes['Em'].edges.value), max(self._response.axes['Em'].edges.value)]
#         #print the energy range considered due to responses:
#         print(f'Energy range considered (by responses design): {self._energy_range[0]} - {self._energy_range[1]} keV')

#         # do a data cut before anything else! actually this should come as a separate routine: data selection and response
#         # prep shold be done before analyzing the data
#         if not type(data) == list:
#             iii = np.where((data['Energies'] >= self._energy_range[0]) & (data['Energies'] <= self._energy_range[1]))
#             self._data = [{key: data[key][iii] for key in data.keys()}]
#         else:
#             data_ecut_list = []
#             for dlist in data:
#                 iii = np.where((dlist['Energies'] >= self._energy_range[0]) & (dlist['Energies'] <= self._energy_range[1]))
#                 data_ecut = {key: dlist[key][iii] for key in dlist.keys()}
#                 data_ecut_list.append(data_ecut)
#             self._data = data_ecut_list

#         self._exposure = sc_orientation.cumulative_livetime().to_value(u.second)

#         self._data_duration = self.get_data_duration()

#         self._data_counts = self.get_data_counts()

#         self._data_azimuthal_angles = self.calculate_azimuthal_scattering_angles(self._data, show_plots=self.SHOW_PLOTS)

#         self._background = background

#         if self._background is not None:
#             print('Background provided. Make sure there is enough statistics.')
#             if not type(background) == list:
#                 iii = np.where((background['Energies'] >= self._energy_range[0]) & (background['Energies'] <= self._energy_range[1]))
#                 self._background = [{key: background[key][iii] for key in background.keys()}]
#             else:
#                 background_ecut_list = []
#                 for bkg in background:
#                     iii = np.where((bkg['Energies'] >= self._energy_range[0]) & (bkg['Energies'] <= self._energy_range[1]))
#                     background_ecut = {key: bkg[key][iii] for key in bkg.keys()}
#                     background_ecut_list.append(background_ecut)
#                 self._background = background_ecut_list

#             self._background_azimuthal_angles = self.calculate_azimuthal_scattering_angles(self._background)
#             self._background_duration = self.get_background_duration()
#         else:
#             print('No background provided. Will not subtract background from data.')
#             self._background = None
#             self._background_duration = 0
#             self._background_azimuthal_angles = None

#         self._mu100 = self.calculate_average_mu100(asad_bin_edges=self.asad_bin_edges, show_plots=False)

#         self._mdp99 = self.calculate_mdp(modulation_factor=self._mu100['mu'])

#     def get_data_counts(self):
#         """
#         Calculate the total counts in the data.

#         Returns
#         -------
#         data_counts : int
#             Total counts in the data
#         """
#         data_counts = 0
#         for i in range(len(self._data)):
#             if type(self._data[i]) == dict:
#                 data_counts += len(self._data[i]['TimeTags'])
#             else:
#                 data_counts += self._data[i].binned_data.axes['Time'].nbins

#         return data_counts

#     def get_data_duration(self):
#         """
#         Calculate the total duration of the data.

#         Returns
#         -------
#         data_duration : float
#             Total duration of the data in seconds
#         """
#         for i in range(len(self._data)):

#             if type(self._data[i]) == dict:

#                 if i == 0:
#                     source_duration = np.max(self._data[i]['TimeTags']) - np.min(self._data[i]['TimeTags'])
#                 else:
#                     source_duration += np.max(self._data[i]['TimeTags']) - np.min(self._data[i]['TimeTags'])

#             else:

#                 if i == 0:
#                     source_duration = (np.max(self._data[i].binned_data.axes['Time'].edges) - np.min(self._data[i].binned_data.axes['Time'].edges)).value
#                 else:
#                     source_duration += (np.max(self._data[i].binned_data.axes['Time'].edges) - np.min(self._data[i].binned_data.axes['Time'].edges)).value

#         return source_duration

#     def get_background_duration(self):
#         """
#         Calculate the total duration of the data.
#         Returns
#         -------
#         background_duration : float
#             Total duration of the data in seconds
#         """
#         if self._background is None:
#             background_duration = 0
#         else:
#             for i in range(len(self._background)):

#                 if type(self._background[i]) == dict:
#                     if i == 0:
#                         background_duration = np.max(self._background[i]['TimeTags']) - np.min(self._background[i]['TimeTags'])
#                     else:
#                         background_duration += np.max(self._background[i]['TimeTags']) - np.min(self._background[i]['TimeTags'])

#                 else:

#                     if i == 0:
#                         background_duration = (np.max(self._background[i].binned_data.axes['Time'].edges) - np.min(self._background[i].binned_data.axes['Time'].edges)).value
#                     else:
#                         background_duration += (np.max(self._background[i].binned_data.axes['Time'].edges) - np.min(self._background[i].binned_data.axes['Time'].edges)).value
#         return background_duration

#     def get_backscal(self):
#         """
#         Calculate the background scaling factor to match the source duration.

#         Returns
#         -------
#         backscal : float
#             Background scaling factor
#         """
#         if self._background_duration == 0:
#             logger.warning('Background duration is zero, returning backscal = 0')
#             backscal = None
#         else:
#             backscal = self._data_duration / self._background_duration

#         return backscal

#     def convolve_spectrum(self, spectrum):
#         """
#         Convolve source spectrum with response and calculate azimuthal scattering angle bins.

#         Parameters
#         ----------
#         response_file : str or pathlib.Path
#             Path to detector response
#         sc_orientation : cosipy.spacecraftfile.SpacecraftFile.SpacecraftFile
#             Spacecraft orientation

#         Returns
#         -------
#         expectation : cosipy.response.PointSourceResponse.PointSourceResponse
#             Expected counts in each bin of Compton data space
#         azimuthal_angle_bins : list
#             Centers of azimuthal scattering angle bins calculated from PsiChi bins in response
#         """
#         polarization_angle = PolarizationAngle(Angle(self._response.axes['Pol'].centers.angle.to_value(u.deg)[0] * u.deg), self._source_vector, convention=self._convention)
#         polarization_level = 0
#         if isinstance(self._convention.frame, SpacecraftFrame):
#             print('>>> Convolving spectrum in spacecraft frame...')
#             target_in_sc_frame = self._ori.get_target_in_sc_frame(target_name='source', target_coord=self._source_vector.transform_to('galactic'))
#             dwell_time_map = self._ori.get_dwell_map(response=self._response_file, src_path=target_in_sc_frame, pa_convention=self._response_convention)
#             psr = self._response.get_point_source_response(exposure_map=dwell_time_map, coord=self._source_vector.transform_to('galactic'))
#             expectation = psr.get_expectation(spectrum, LinearPolarization(polarization_level * 100., polarization_angle.angle.deg))

#             azimuthal_angle_bins = []

#             for i in range(expectation.axes['PsiChi'].nbins):
#                 psichi = SkyCoord(lat=(np.pi/2) - expectation.axes['PsiChi'].pix2ang(i)[0], lon=expectation.axes['PsiChi'].pix2ang(i)[1], unit=u.rad, frame=self._convention.frame)
#                 azimuthal_angle = PolarizationAngle.from_scattering_direction(psichi, self._source_vector, self._convention)
#                 azimuthal_angle_bins.append(azimuthal_angle.angle)

#         else:
#             print('>>> Convolving spectrum in ICRS frame...')
#             scatt_map = self._ori.get_scatt_map(nside=self._response.nside*2, target_coord=self._source_vector)
#             # scatt_map = self._ori.get_scatt_map(nside=self._response.nside*2, target_coord=self._source_vector, coordsys='galactic')
#             psr = self._response.get_point_source_response(coord=self._source_vector, scatt_map=scatt_map)
#             expectation = psr.get_expectation(spectrum, LinearPolarization(polarization_level * 100., polarization_angle.angle.deg))

#             azimuthal_angle_bins = []

#             for i in range(expectation.axes['PsiChi'].nbins):
#                 psichi = expectation.axes['PsiChi'].pix2skycoord(i).transform_to('icrs')
#                 azimuthal_angle = PolarizationAngle.from_scattering_direction(psichi, self._source_vector, self._convention)
#                 azimuthal_angle_bins.append(azimuthal_angle.angle)

#         return expectation, azimuthal_angle_bins

#     def calculate_azimuthal_scattering_angles(self, unbinned_data, show_plots=False):
#         """
#         Calculate the azimuthal scattering angles for all events in a dataset.

#         Parameters
#         ----------
#         unbinned_data : dict
#             Unbinned data including polar and azimuthal angles (radians) of scattered photon in local coordinates

#         Returns
#         -------
#         azimuthal_angles : list of astropy.coordinates.Angle
#             Azimuthal scattering angles
#         """
#         azimuthal_angles = []

#         if isinstance(self._convention.frame, SpacecraftFrame):
#             for i in range(len(unbinned_data['Psi local'])):
#                 # if unbinned_data['Energies'][i] >= self._energy_range[0] and unbinned_data['Energies'][i] <= self._energy_range[1]:
#                 psichi = SkyCoord(lat=(np.pi/2) - unbinned_data['Psi local'][i], lon=unbinned_data['Chi local'][i], unit=u.rad, frame=self._convention.frame)
#                 azimuthal_angle = PolarizationAngle.from_scattering_direction(psichi, self._source_vector, self._convention)
#                 azimuthal_angles.append(azimuthal_angle.angle)
#         else:
#             if len(unbinned_data) < 2:

#                 for i in range(len(unbinned_data[0]['Psi galactic'])):
#                     # if unbinned_data[0]['Energies'][i] >= self._energy_range[0] and unbinned_data[0]['Energies'][i] <= self._energy_range[1]:
#                     psichi = SkyCoord(l=unbinned_data[0]['Chi galactic'][i], b=unbinned_data[0]['Psi galactic'][i], frame='galactic', unit=u.deg).transform_to('icrs')
#                     azimuthal_angle = PolarizationAngle.from_scattering_direction(psichi, self._source_vector, self._convention)
#                     azimuthal_angles.append(azimuthal_angle.angle)
#             else:
#                 for j in range(len(unbinned_data)):
#                     for i in range(len(unbinned_data[j]['Psi galactic'])):
#                         # if unbinned_data[j]['Energies'][i] >= self._energy_range[0] and unbinned_data[j]['Energies'][i] <= self._energy_range[1]:
#                         psichi = SkyCoord(l=unbinned_data[j]['Chi galactic'][i], b=unbinned_data[j]['Psi galactic'][i], frame='galactic', unit=u.deg).transform_to('icrs')
#                         azimuthal_angle = PolarizationAngle.from_scattering_direction(psichi, self._source_vector, self._convention)
#                         azimuthal_angles.append(azimuthal_angle.angle)

#         if show_plots:
#             plt.figure()
#             plt.title('Azimuthal scattering angles')
#             plt.hist(azimuthal_angles, bins=50, alpha=0.5, label='Data fine binning')
#             plt.hist(azimuthal_angles, bins=self._nbins, alpha=0.5,
#                      histtype='step', linewidth=2, label='Response binning')
#             plt.xlabel('Azimuthal angle (radians)')
#             plt.ylabel('Counts')
#             plt.legend()
#             plt.show()

#         return azimuthal_angles

#     def calculate_average_mu100(self, asad_bin_edges=None, show_plots=False):
#         """
#         Calculate the modulation (mu) of an 100% polarized source.

#         Parameters
#         ----------
#         asad_bin_edges : array-like, optional
#             Bin edges for the ASAD. If None, default binning is used.
#         show_plots : bool, optional
#             Option to show plots. Default is False

#         Returns
#         -------
#         mu_100 : dict
#             Modulation of 100% polarized source and uncertainty of constant function fit to modulation in all polarization angle bins
#         """

#         if asad_bin_edges is not None:
#             self._nbins = asad_bin_edges
#             print('Custom Number of azimuthal angle bins used:', self._nbins)

#         print('Creating the 100% polarized ASADs (this may take a minute...)')
#         polarized_asads = create_polarized_asads(self._spectrum, self._source_vector, self._ori, self._response,
#                                                 self._convention, self._response_file, self._response_convention, bins=self._nbins)
#         print('Creating the unpolarized ASAD...')
#         unpolarized_asad = create_unpolarized_asad(self._spectrum, self._source_vector, self._ori, self._response,
#                                                     self._convention, self._response_file, self._response_convention, bins=self._nbins)
#         mu_100_list = []
#         mu_100_uncertainties = []

#         for i in range(self._response.axes['Pol'].nbins):
#             logger.info('Polarization angle bin: ' + str(self._response.axes['Pol'].edges.angle.to_value(u.deg)[i]) + ' to ' + str(self._response.axes['Pol'].edges.angle.to_value(u.deg)[i+1]) + ' deg')
#             asad_corrected = polarized_asads[i] / np.sum(polarized_asads[i]) / unpolarized_asad * np.sum(unpolarized_asad)
#             mu, mu_err = get_modulation(asad_corrected.axis.centers.value, asad_corrected.full_contents,
#                                         title='Modulation PA bin %i'%i, show=show_plots)
#             mu_100_list.append(mu)
#             mu_100_uncertainties.append(mu_err)

#         popt, pcov = curve_fit(constant, self._response.axes['Pol'].centers.angle.to_value(u.deg), mu_100_list,
#                                sigma=mu_100_uncertainties, p0=np.mean(mu_100_list), absolute_sigma=True)
#         mu_100 = {'mu': popt[0], 'uncertainty': pcov[0][0]}

#         if show_plots == True:
#             plt.figure()
#             plt.scatter(self._response.axes['Pol'].centers.angle.to_value(u.deg), mu_100_list)
#             plt.errorbar(self._response.axes['Pol'].centers.angle.to_value(u.deg), mu_100_list,
#                          yerr=mu_100_uncertainties, linewidth=0, elinewidth=1)
#             plt.plot([0, 175], [mu_100['mu'], mu_100['mu']])
#             plt.xlabel('Polarization Angle (degrees)')
#             plt.ylabel('mu_100')
#             plt.show()

#         return mu_100

#     def compute_data_pseudo_stokes(self, show_plots=False):
#         """
#         Calculates photon-by-photon pseudo stokes parameters from the photon azimutal angle.

#         Parameters
#         ----------
#         show : bool, optional
#             If True, display a diagnostic plot in the Q-U plane with
#             uncertainty circles, by default False.

#         Returns
#         -------
#         qs : list
#             list of pseudo-q parameters for each photon (ordered as input array)
#         us : list
#             list of pseudo-u parameters for each photon (ordered as input array)
#         """

#         qs, us = [], []
#         ######################
#         # ATTENTION: I need to add 90 degrees because the stokes convention assumes that EVPA //
#         # source polarization, while for Compton scatttering it is perpendicular)
#         try:
#             for a in self._data_azimuthal_angles.value:
#                 qs.append(stokes_q(a - np.pi/2))
#                 us.append(stokes_u(a - np.pi/2))
#         except:
#             a_ = np.concatenate(self._data_azimuthal_angles)
#             for a in a_:
#                 qs.append(stokes_q(a.value - np.pi/2))
#                 us.append(stokes_u(a.value - np.pi/2))

#         if show_plots:
#             plt.figure()
#             plt.title('Source Stokes parameters (%i events)'%len(qs))
#             plt.hist(qs, bins=50, alpha=0.5, label='q$_s$')
#             plt.hist(us, bins=50, alpha=0.5, label='u$_s$')
#             plt.xlabel('Pseudo Stokes parameter')
#             plt.legend()
#             plt.show()

#         return qs, us

#     def compute_background_pseudo_stokes(self, show_plots=False):
#         """
#         Calculates photon-by-photon pseudo stokes parameters from the photon azimutal angle.

#         Parameters
#         ----------
#         azimuthal_angles : list
#             Azimuthal scattering angles (radians)

#         Returns
#         -------
#         qs : list
#             list of pseudo-q parameters for each photon (ordered as input array)
#         us : list
#             list of pseudo-u parameters for each photon (ordered as input array)
#         """

#         qs, us = [], []

#         if self._background_azimuthal_angles is None:
#             logger.warning('No background data provided, returning empty lists for pseudo Stokes parameters.')
#             return 0

#         else:
#             try:
#                 for a in self._background_azimuthal_angles.value:
#                     qs.append(stokes_q(a - np.pi/2))
#                     us.append(stokes_u(a - np.pi/2))
#             except:
#                 a_ = np.concatenate(self._background_azimuthal_angles)
#                 for a in a_:
#                     qs.append(stokes_q(a.value - np.pi/2))
#                     us.append(stokes_u(a.value - np.pi/2))

#             if show_plots:
#                 plt.figure()
#                 plt.title('Background Stokes parameters (%i events)'%len(qs))
#                 plt.hist(qs, bins=50, alpha=0.5, label='q$_b$')
#                 plt.hist(us, bins=50, alpha=0.5, label='u$_b$')
#                 plt.xlabel('Pseudo Stokes parameter')
#                 plt.legend()
#                 plt.show()

#         return qs, us

#     def calculate_mdp(self, modulation_factor):
#         """
#         Calculate the minimum detectable polarization (MDP) of the source.

#         Returns
#         -------
#         mdp : float
#             MDP of source
#         """
#         if not type(self._data) == list:
#             source_counts = 0
#             for i in range(len(self._data)):
#                 source_counts += len(self._data[i]['TimeTags'])
#         else:
#             source_counts = len(self._data[0]['TimeTags'])
#             source_data_rate = source_counts / self._data_duration

#         if self._background is not None:
#             if type(self._background) == list:
#                 background_counts = 0
#                 for i in range(len(self._background)):
#                     background_counts += len(self._background[i]['TimeTags'])
#             else:
#                 background_counts = self._background[0]['TimeTags']

#             background_data_rate = background_counts / self._background_duration
#             mdp = 4.29 /  modulation_factor * np.sqrt(source_data_rate/self._data_duration + background_data_rate/self._background_duration) / source_data_rate
#         else:
#             mdp = 4.29 /  modulation_factor / np.sqrt(source_counts)

#         logger.info('Minimum detectable polarization (MDP) of source: ' + str(round(mdp, 3)))

#         return mdp

#     def calculate_polarization(self, qs, us, mu, bkg_qs=None, bkg_us=None, show_plots=False, ref_qu=(None, None),
#                                ref_pdpa=(None, None), ref_label=None, mdp=None):
#         """
#         Calculate the polarization degree (PD), polarization angle (PA),
#         and their associated 1-sigma uncertainties given Q and U measurements
#         from both polarized and unpolarized data sets.

#         This implements equations (21), (22), (36), and (37) from Kislat et al. (2015).

#         Parameters
#         ----------
#         qs : array-like
#             Array of Q measurements (from polarized source).
#         us : array-like
#             Array of U measurements (from polarized source).
#         mu : float
#             Modulation factor. Used to convert raw measurements into normalized Q/I and U/I.
#         bkg_qs : array-like, optional
#             Array of Q measurements from unpolarized background or simulation data, by default None.
#         bkg_us : array-like, optional
#             Array of U measurements from unpolarized background or simulation data, by default None.
#         show_plots : bool, optional
#             If True, display a diagnostic plot in the Q-U plane with
#             uncertainty circles, by default False.
#         ref_qu : tuple of (float or None, float or None), optional
#             Reference (Q, U) point (e.g., from simulation) to be plotted for comparison,
#             by default (None, None) (no reference shown).
#         ref_pdpa : tuple of (float or None, float or None), optional
#             Reference (PD, PA) point (e.g., from simulation) to be converted to Q/U
#             and plotted for comparison, by default (None, None) (no reference shown).
#         ref_label : str, optional
#             Label for the reference point in the plot, by default None (no label shown).
#         mdp : float, optional
#             Minimum detectable polarization (MDP) value to be used for uncertainty calculations,
#             by default None (no MDP used).

#         Returns
#         -------
#         polarization: dict

#             fraction : float
#                 Polarization degree, PD = sqrt(Q^2 + U^2).
#             fraction_uncertainty : float
#                 1-sigma statistical uncertainty on the polarization degree.
#             angle : astropy.coordinates.Angle
#                 Polarization angle (in radians internally),
#                 computed as 90 - 0.5 * arctan2(U, Q) (converted into an Angle object).
#             angle_uncertainty : float
#                 1-sigma statistical uncertainty on the polarization angle (in degrees).
#         """
#         BACKSCAL = self.get_backscal()

#         if BACKSCAL is None:
#             logger.warning('Background scaling factor is None, assuming the unpolarized signal'+
#                            'has been simulated with the same statistics as THE data')
#             BACKSCAL = 1

#         pol_I = I = len(qs)
#         pol_Q = np.sum(qs) / mu
#         pol_U = np.sum(us) / mu
#         print('I, Q, U, mu', pol_I, pol_Q, pol_U, mu)

#         self.QN = pol_Q/pol_I
#         self.UN = pol_U/pol_I
#         print('Q, U (unsubtracted:)', self.QN, self.UN)

#         if bkg_qs is None or bkg_us is None:
#             print('No background data provided, assuming no background contribution.')
#         else:
#             print('Unpolarized bkg (or simulation) provided, subtracting its contribution.')
#             bkg_qs = np.array(bkg_qs)
#             bkg_us = np.array(bkg_us)
#             if bkg_qs.ndim == 1:
#                 unpol_I = len(bkg_qs) * BACKSCAL
#                 unpol_Q = np.sum(bkg_qs) * BACKSCAL / mu
#                 unpol_U = np.sum(bkg_us) * BACKSCAL / mu
#                 I = pol_I - unpol_I
#                 print('check I(src+bkg) vs I(src):', pol_I, I)
#             else:
#                 BACKSCAL = 1
#                 unpol_I = []
#                 unpol_Q = []
#                 unpol_U = []
#                 for i in range(len(bkg_qs)):
#                     unpol_I.append(len(bkg_qs[i]) * BACKSCAL)
#                     unpol_Q.append(np.sum(bkg_qs[i]) * BACKSCAL / mu)
#                     unpol_U.append(np.sum(bkg_us[i]) * BACKSCAL / mu)
#                 unpol_I = np.mean(unpol_I)
#                 unpol_Q = np.mean(unpol_Q)
#                 unpol_U = np.mean(unpol_U)
#             # print('I unpolarized:', unpol_I)
#             print('Q, U unpolarized:', unpol_Q/unpol_I, unpol_U/unpol_I)
#             unpol_modulation = mu * np.sqrt(unpol_Q**2. + unpol_U**2.) / unpol_I
#             unpol_sI = np.sqrt(unpol_I)
#             unpol_sQ = np.sqrt((2 - unpol_modulation**2) * unpol_sI**2 / unpol_I**2 / mu**2)
#             unpol_sU = np.sqrt((2 - unpol_modulation**2) * unpol_sI**2 / unpol_I**2 / mu**2)
#             print('Q, U unpolarized uncertainty:', unpol_sQ*100, '%')

#             self.QN = np.sum([pol_Q/pol_I, unpol_Q/unpol_I * BACKSCAL])
#             self.UN = np.sum([pol_U/pol_I, unpol_U/unpol_I * BACKSCAL])

#             print('Q, U, subtracted:', self.QN, self.UN)


#         pol_sI = np.sqrt(I)
#         pol_sQ = np.sqrt((2 - self.QN**2) * pol_sI**2 / I**2 / mu**2)
#         pol_sU = np.sqrt((2 - self.UN**2) * pol_sI**2 / I**2 / mu**2)
#         pol_covQNUN = - (self.QN * self.UN) / I**2
#         print('Q/I, U/I, uncertainty:', pol_sQ, pol_sU, np.sqrt(pol_sQ))

#         # Reconstructed polarization fraction uncertainty: See eq 36 in Kislat 2015
#         polarization_fraction = np.sqrt(self.QN**2. + self.UN**2.)
#         m = mu * polarization_fraction
#         polarization_fraction_uncertainty = np.sqrt((2 - m**2)/((I - 1) * mu**2))
#         pol_PD = polarization_fraction * 100
#         pol_1sigmaPD = polarization_fraction_uncertainty * 100

#         # Reconstructed polarization angle uncertainty: See eq 37 in Kislat 2015
#         pol_PA = 0.5 * np.arctan2(self.UN, self.QN)
#         # Convert to 0 to 180 deg (just the convention)
#         if pol_PA < 0:
#             pol_PA += np.pi

#         pol_1sigmaPA = np.degrees(1 / (m * np.sqrt(2. * (I - 1.))))
#         print('\n ############################## \n')
#         print('     PD: %.2f'%(pol_PD), '+/- %.2f'%(pol_1sigmaPD), '%')
#         print('     PA: %.2f'%(np.degrees(pol_PA)), '+/- %.2f'%pol_1sigmaPA, 'deg')
#         print('\n ############################## \n')

#         if show_plots:

#             fig, ax = plt.subplots(figsize=(6.7, 6.4))

#             polar_chart_backbone(ax)

#             if ref_qu[0] != None:
#                 # print('Drawing Reference point:', ref_qu)
#                 plt.plot(ref_qu[0], ref_qu[1], 'x', markersize=20, color='tab:green')
#                 plt.annotate(ref_label, (ref_qu[0], ref_qu[1]), textcoords="offset points", xytext=(0,10),
#                              ha='center', fontsize=12)
#             if ref_pdpa[0] != None:
#                 # print('Drawing Reference point:', ref_pdpa)
#                 ref_q, ref_u = rotate_points_to_x_axis(ref_pdpa[0], np.radians(ref_pdpa[1]))
#                 plt.plot(ref_q, ref_u, 'x', markersize=20, color='tab:green')
#                 plt.annotate(ref_label, (ref_q, ref_u), textcoords="offset points", xytext=(0,10), ha='center',
#                              color='tab:green', fontsize=12)

#             if mdp != None:
#                 c_mdp = plt.Circle((0, 0), radius=mdp, facecolor='tab:red', alpha=0.3, linewidth=1, linestyle='--',
#                                    label=r'MDP$_{99}$ = %.2f %%'%(self._mdp99*100))
#                 plt.gca().add_artist(c_mdp)


#             if bkg_qs is None or bkg_us is None:
#                 label_data = ("PD = (%.1f ± %.1f)%%\n"
#                               "PA = (%.1f ± %.1f) deg"
#                              % (pol_PD, pol_1sigmaPD, np.degrees(pol_PA), pol_1sigmaPA) )
#                 pass
#             else:
#                 label_data = ("Measured (Unpol subtracted)\n"
#                           "PD = (%.1f ± %.1f)%%\n"
#                           "PA = (%.1f ± %.1f) deg"
#                           % (pol_PD, pol_1sigmaPD, np.degrees(pol_PA), pol_1sigmaPA) )
#                 plt.plot(unpol_Q/unpol_I, unpol_U/unpol_I,  'o', markersize=5, color='0.4', \
#                         label=r'Unpol (PD$_{1\sigma}$ = %i %%)'%(unpol_sQ*100))
#                 unpol_c = plt.Circle((unpol_Q/unpol_I, unpol_U/unpol_I), radius=unpol_sQ, facecolor='none', edgecolor='0.4', linewidth=1)
#                 unpol_c2 = plt.Circle((unpol_Q/unpol_I, unpol_U/unpol_I), radius=2*unpol_sQ, facecolor='none', edgecolor='0.4', linewidth=1)
#                 unpol_c3 = plt.Circle((unpol_Q/unpol_I, unpol_U/unpol_I), radius=3*unpol_sQ, facecolor='none', edgecolor='0.4', linewidth=1)
#                 plt.gca().add_artist(unpol_c)
#                 plt.gca().add_artist(unpol_c2)
#                 plt.gca().add_artist(unpol_c3)

#             plt.plot(self.QN, self.UN, 'o', markersize=5, color='red', label=label_data)
#             pol_c = plt.Circle((self.QN, self.UN), radius=polarization_fraction_uncertainty, facecolor='none', edgecolor='red', linewidth=1)
#             pol_c2 = plt.Circle((self.QN, self.UN), radius=2*polarization_fraction_uncertainty, facecolor='none', edgecolor='red', linewidth=1)
#             pol_c3 = plt.Circle((self.QN, self.UN), radius=3*polarization_fraction_uncertainty, facecolor='none', edgecolor='red', linewidth=1)
#             plt.gca().add_artist(pol_c)
#             plt.gca().add_artist(pol_c2)
#             plt.gca().add_artist(pol_c3)

#             plt.xlim(-1, 1)
#             plt.ylim(-1, 1)
#             plt.xlabel('Q/I')
#             plt.ylabel('U/I')
#             plt.tight_layout()
#             plt.legend(fontsize=12)

#             plt.show()

#         polarization_angle = Angle(np.degrees(pol_PA), unit=u.deg)
#         polarization_angle = PolarizationAngle(polarization_angle, self._source_vector, convention=self._convention).transform_to(IAUPolarizationConvention())
#         polarization_angle_uncertainty = Angle(pol_1sigmaPA, unit=u.deg)

#         polarization = {'fraction': polarization_fraction,
#                         'angle': polarization_angle,
#                         'fraction_uncertainty': polarization_fraction_uncertainty,
#                         'angle_uncertainty': polarization_angle_uncertainty,
#                         'QN': self.QN,
#                         'UN': self.UN,
#                         'QN_ERR': pol_sQ,
#                         'UN_ERR': pol_sU}

#         return polarization


# if __name__ == "__main__":

#     print('Just some tests here...')

#     pass



# MAB ////////////////////////////////////////////////////////////////////////////////////////////

import numpy as np
from astropy.coordinates import Angle, SkyCoord
import astropy.units as u
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from cosipy.polarization.polarization_angle import PolarizationAngle
from cosipy.polarization.conventions import MEGAlibRelativeX, MEGAlibRelativeY, MEGAlibRelativeZ, IAUPolarizationConvention
from cosipy.response import FullDetectorResponse
from scoords import SpacecraftFrame
from threeML import LinearPolarization
import scipy.interpolate as interpolate
from histpy import Histogram

import logging
logger = logging.getLogger(__name__)

#we can define all these functions in a separate file to import

def R(x, A, B, C):
    """ Function to fit to the modulation of the azimuthal angle distribution.
    """
    return A + B*(np.cos(x + C)**2)

def constant(x, a):
        """
        Constant function to fit to mu_100 values.

        Parameters
        ----------
        x : float
            Mu_100
        a : float
            Parameter

        Returns
        -------
        a : float
            Constant value
        """

        return a

def stokes_u(phi):
    """
    Calculate the U Stokes parameter from the azimuthal angle phi.

    Parameters
    ----------
    phi : float
        Azimuthal angle in radians

    Returns
    -------
    u : float
        U Stokes parameter
    """
    return np.sin(phi * 2) * 2

def stokes_q(phi):
    """
        Calculate the Q Stokes parameter from the azimuthal angle phi.

        Parameters
        ----------
        phi : float
            Azimuthal angle in radians

        Returns
        -------
        q : float
            Q Stokes parameter
        """
    return np.cos(phi * 2) * 2

def rotate_points_to_x_axis(newPD, newPA):
    """
    Rotate arrays of points (x_, y_) in the QN-UN plane by an angle

    Parameters
    ----------
    newPD : float
        Polarization degree
    newPA : float
        Polarization angle
    Returns
    -------
    rotated_Q : float
        Q Stokes parameter
    rotated_U : float
        U Stokes parameter

    """
    # Create a matrix of rotation matrices for each point
    rotated_Q = newPD * np.cos(2 * newPA)
    rotated_U = newPD * np.sin(2 * newPA)

    return rotated_Q, rotated_U

def polar_chart_backbone(ax):
    """ Preparing canvas for Stokes chart
    Parameters
    ----------
    ax : matplotlib.axes._axes.Axes
        Axes to plot on
    """
    ax.spines['top'].set_visible(True)
    ax.spines['right'].set_visible(True)
    c0 = plt.Circle((0,0), radius=0.25, facecolor='none', edgecolor='k', linewidth=1, linestyle='--', alpha=0.3)
    c1 = plt.Circle((0,0), radius=0.50, facecolor='none', edgecolor='k', linewidth=1, linestyle='--', alpha=0.3)
    c2 = plt.Circle((0,0), radius=0.75, facecolor='none', edgecolor='k', linewidth=1, linestyle='--', alpha=0.3)
    c3 = plt.Circle((0,0), radius=1.00, facecolor='none', edgecolor='k', linewidth=1, linestyle='-', alpha=0.5)
    plt.gca().add_artist(c0)
    plt.gca().add_artist(c1)
    plt.gca().add_artist(c2)
    plt.gca().add_artist(c3)
    plt.annotate('0.25', (0.25, 0), textcoords="offset points", xytext=(10,0), ha='center', fontsize=8, color='k', alpha=0.3)
    plt.annotate('0.50', (0.50, 0), textcoords="offset points", xytext=(10,0), ha='center', fontsize=8, color='k', alpha=0.3)
    plt.annotate('0.75', (0.75, 0), textcoords="offset points", xytext=(10,0), ha='center', fontsize=8, color='k', alpha=0.3)
    plt.annotate('1.00', (1.00, 0), textcoords="offset points", xytext=(10,0), ha='center', fontsize=8, color='k', alpha=0.3)
    plt.hlines(0, -1, 1, linewidth=1, color='k', linestyle='--', alpha=0.3)
    plt.vlines(0, -1, 1, linewidth=1, color='k', linestyle='--', alpha=0.3)
    plt.plot([1,-1], [1,-1], linewidth=1, color='k', linestyle='--', alpha=0.3)
    plt.plot([1,-1], [-1,1], linewidth=1, color='k', linestyle='--', alpha=0.3)

def calculate_azimuthal_scattering_angle(psi, chi, source_vector, reference_vector):
    """Vectorized signed azimuthal scattering angle calculation."""
    psi = np.asarray(psi, dtype=float)
    chi = np.asarray(chi, dtype=float)
    psi, chi = np.broadcast_arrays(psi, chi)

    scattered = np.stack(
        (np.sin(psi) * np.cos(chi),
         np.sin(psi) * np.sin(chi),
         np.cos(psi)),
        axis=-1,
    )

    source = np.asarray(source_vector.cartesian.xyz.value, dtype=float).reshape(3)
    reference = np.asarray(reference_vector.cartesian.xyz.value, dtype=float).reshape(3)
    source /= np.linalg.norm(source)

    # Ensure the reference vector lies in the plane normal to the source.
    reference = reference - np.dot(reference, source) * source
    reference_norm = np.linalg.norm(reference)
    if reference_norm == 0:
        raise ValueError("reference_vector is parallel to source_vector")
    reference /= reference_norm

    projection = scattered - np.einsum("...i,i->...", scattered, source)[..., None] * source
    projection_norm = np.linalg.norm(projection, axis=-1)
    valid = projection_norm > np.finfo(float).eps

    projection_unit = np.full_like(projection, np.nan, dtype=float)
    projection_unit[valid] = projection[valid] / projection_norm[valid, None]

    x = np.clip(np.einsum("...i,i->...", projection_unit, reference), -1.0, 1.0)
    y = np.einsum("i,...i->...", source, np.cross(projection_unit, reference))
    return Angle(np.arctan2(y, x), unit=u.rad)

def get_modulation(_x, _y, title='Modulation', show=False):
    """ Function to estimate the modulation factor.
        _x is the central value of the histogram bins
        _y is the value of the bins on the histograms

        Parameters
        ----------
        _x : array
            Central values of the histogram bins
        _y : array
            Values of the histogram bins
        title : str
            Title of the plot
        show : bool
            Whether to show the plot or not

        Returns
        -------
        mu : float
            Modulation factor
        mu_err : float
            Error on the modulation factor
    """

    popt, pcov = curve_fit(R, _x, _y ) #sigma=np.sqrt(_y), absolute_sigma=True
    pcov[0][0], pcov[1][1], pcov[2][2] = np.sqrt(pcov[0][0]), np.sqrt(pcov[1][1]), np.sqrt(pcov[2][2])
    print('A = %.2f, B = %.2f, C = %.2f'%(popt[0], popt[1], popt[2]))

    Rmax, Rmin = np.amax(R(_x, *popt)), np.amin(R(_x, *popt))
    print('Rmax, Rmin:', Rmax, Rmin)
    mu = (Rmax-Rmin)/(Rmax+Rmin)
    print('Modulation mu = ', mu)

    mu_err = 2/(popt[1]+2*popt[0])**2 * np.sqrt(popt[1]**2 * pcov[0][0]**2 + popt[0]**2 * pcov[1][1]**2)

    if show:

        plt.figure()
        plt.title(title)
        plt.step(_x, _y, where='mid')
        perr = [popt[0]+np.sqrt(pcov[0][0]), popt[1]+np.sqrt(pcov[1][1]), popt[2]]
        merr = [popt[0]-np.sqrt(pcov[0][0]), popt[1]-np.sqrt(pcov[1][1]), popt[2]]
        plt.fill_between(_x, R(_x, *perr), R(_x, *merr), color='red', alpha=0.3)
        plt.plot(_x, R(_x, *popt), 'r-', label=r'$\mu=$%.3f'%(mu))
        plt.legend(fontsize=12)
        plt.xlabel('Azimuthal angle [rad]')
        plt.savefig('%s'%title)

    return mu, mu_err

def create_asad_from_response(spectrum, polarization_level, polarization_angle, source_vector, ori, response,
                              convention, response_file, response_convention, bins=20):
    """Create an ASAD from the response using vectorized angle binning."""
    if isinstance(convention.frame, SpacecraftFrame):
        source_gal = source_vector.transform_to("galactic")
        target_in_sc_frame = ori.get_target_in_sc_frame(
            target_name="source", target_coord=source_gal
        )
        dwell_time_map = ori.get_dwell_map(
            response=response_file,
            src_path=target_in_sc_frame,
            pa_convention=response_convention,
        )
        psr = response.get_point_source_response(
            exposure_map=dwell_time_map, coord=source_gal
        )
    else:
        scatt_map = ori.get_scatt_map(
            nside=response.nside * 2, target_coord=source_vector
        )
        psr = response.get_point_source_response(
            coord=source_vector, scatt_map=scatt_map
        )

    expectation = psr.get_expectation(
        spectrum,
        LinearPolarization(
            polarization_level * 100.0,
            polarization_angle.angle.deg,
        ),
    )

    psichi_axis = expectation.axes["PsiChi"]
    pixel_indices = np.arange(psichi_axis.nbins)

    if isinstance(convention.frame, SpacecraftFrame):
        try:
            theta, phi = psichi_axis.pix2ang(pixel_indices)
        except Exception:
            theta_phi = np.asarray([psichi_axis.pix2ang(i) for i in pixel_indices])
            theta, phi = theta_phi[:, 0], theta_phi[:, 1]
        scattering_directions = SkyCoord(
            lat=(np.pi / 2.0) - theta,
            lon=phi,
            unit=u.rad,
            frame=convention.frame,
        )
    else:
        try:
            scattering_directions = psichi_axis.pix2skycoord(pixel_indices).transform_to("icrs")
        except Exception:
            scattering_directions = SkyCoord([
                psichi_axis.pix2skycoord(i).transform_to("icrs")
                for i in pixel_indices
            ])

    reference_vector = convention.get_basis(source_vector)[0]
    scattering_cart = np.asarray(scattering_directions.cartesian.xyz.value, dtype=float).T
    source_cart = np.asarray(source_vector.cartesian.xyz.value, dtype=float).reshape(3)
    reference_cart = np.asarray(reference_vector.cartesian.xyz.value, dtype=float).reshape(3)
    source_cart /= np.linalg.norm(source_cart)
    reference_cart -= np.dot(reference_cart, source_cart) * source_cart
    reference_cart /= np.linalg.norm(reference_cart)

    projection = scattering_cart - (scattering_cart @ source_cart)[:, None] * source_cart
    projection_norm = np.linalg.norm(projection, axis=1)
    valid = projection_norm > np.finfo(float).eps
    projection_unit = np.full_like(projection, np.nan)
    projection_unit[valid] = projection[valid] / projection_norm[valid, None]
    x = np.clip(projection_unit @ reference_cart, -1.0, 1.0)
    y = np.einsum("i,ni->n", source_cart, np.cross(projection_unit, reference_cart))
    azimuthal_angles = np.arctan2(y, x)

    if isinstance(bins, int):
        if bins < 1:
            raise ValueError("bins must be a positive integer")
        bin_edges_rad = np.linspace(-np.pi, np.pi, bins + 1)
    else:
        bin_edges_rad = Angle(bins).to_value(u.rad)
        if bin_edges_rad.ndim != 1 or bin_edges_rad.size < 2:
            raise ValueError("bins must contain at least two bin edges")

    projected = expectation.project(["PsiChi"])
    if hasattr(projected, "full_contents"):
        weights = np.asarray(projected.full_contents, dtype=float).reshape(-1)
    elif hasattr(projected, "contents"):
        weights = np.asarray(projected.contents, dtype=float).reshape(-1)
    else:
        weights = np.asarray([projected[i] for i in range(projected.nbins)], dtype=float)

    if weights.size != azimuthal_angles.size:
        raise ValueError(
            f"PsiChi projection has {weights.size} values, but {azimuthal_angles.size} angles were calculated"
        )

    finite = np.isfinite(azimuthal_angles) & np.isfinite(weights)
    asad_contents, _ = np.histogram(
        azimuthal_angles[finite], bins=bin_edges_rad, weights=weights[finite]
    )
    return Histogram(Angle(bin_edges_rad, unit=u.rad), contents=asad_contents)

def create_unpolarized_asad(spectrum, source_vector, ori, response, convention, response_file, response_convention, bins=20):
        """
        Create unpolarized ASAD from response.

        Parameters
        ----------
        bins : int or astropy.units.quantity.Quantity, optional
            Number of azimuthal scattering angle bins if int or array of edges of azimuthal scattering angle bins if Quantity
        spectrum : :py:class:`threeML.Model`
            Spectral model.
        source_vector : astropy.coordinates.sky_coordinate.SkyCoord
            Source direction:
        ori : cosipy.spacecraftfile.SpacecraftFile.SpacecraftFile
            Spacecraft orientation
        response : cosipy.response.FullDetectorResponse.FullDetectorResponse
            Response object
        convention : cosipy.polarization.PolarizationConvention
            Polarization convention
        response_file : str or pathlib.Path
            Path to detector response
        response_convention : str
            Response convention. If in the spacecraft frame, the angle must have the same convention as the response.
        Returns
        -------
        asad : histpy.Histogram
            Counts in each azimuthal scattering angle bin
        """
        pd = 0
        pa = PolarizationAngle(Angle(0 * u.deg), source_vector, convention=convention)
        unpolarized_asad = create_asad_from_response(spectrum, pd, pa, source_vector, ori,
                                                     response, convention, response_file,
                                                     response_convention, bins=bins)

        return unpolarized_asad

def create_polarized_asads(spectrum, source_vector, ori, response, convention, response_file, response_convention, bins=20):
        """
        Create 100% polarized ASADs for each polarization angle bin of response.

        Parameters
        ----------
        bins : int or astropy.units.quantity.Quantity, optional
            Number of azimuthal scattering angle bins if int or array of edges of azimuthal scattering angle bins if Quantity

        Returns
        -------
        polarized_asads : dict of histpy.Histogram
            Counts in each azimuthal scattering angle bin for each polarization angle bin
        """

        polarized_asads = {}
        for k in range(response.axes['Pol'].nbins):
            pd = 1
            pa = PolarizationAngle(Angle(response.axes['Pol'].centers.angle.to_value(u.deg)[k] * u.deg), source_vector, convention=convention)
            polarized_asads[k] = create_asad_from_response(spectrum, pd, pa, source_vector, ori,
                                                            response, convention, response_file,
                                                            response_convention, bins=bins)
        return polarized_asads

class PolarizationStokes():
    """
    Stokes parameter method to fit polarization.

    Parameters
    ----------
    source_vector : astropy.coordinates.sky_coordinate.SkyCoord
        Source direction
    source_spectrum : astromodels.functions.functions_1D
        Spectrum of source

    data : list of dict
        Data to fit
    background : list of dict
        Background to fit
    response_convention : str
        Response convention
    response_file : str or pathlib.Path
        Path to detector response
    sc_orientation : cosipy.spacecraftfile.SpacecraftFile.SpacecraftFile
        Spacecraft orientation
    fit_convention : cosipy.polarization.PolarizationConvention
        Polarization convention for the fit
    show_plots : bool
        Whether to show plots or not
    """


    def __init__(self, source_vector, source_spectrum, data,
                 response_file, sc_orientation, background=None, response_convention='RelativeX',
                 fit_convention=IAUPolarizationConvention(), asad_bin_edges=None, show_plots=False):

        ###################### This will need to be changed into IAUPolarizationConvention hardcoded!
        ######################
        print('This class loading takes around 30 seconds... \n')
        ######################

        if isinstance(fit_convention.frame, SpacecraftFrame) and not isinstance(source_vector.frame, SpacecraftFrame):
            attitude = sc_orientation.get_attitude()[0]
            source_vector = source_vector.transform_to(SpacecraftFrame(attitude=attitude))
            logger.warning('The source direction is being converted to the spacecraft frame using the attitude at the first timestamp of the orientation.')
        elif not isinstance(fit_convention.frame, SpacecraftFrame):
            source_vector = source_vector.transform_to('icrs')

        if ((isinstance(fit_convention, MEGAlibRelativeX) and response_convention != 'RelativeX') or
            (isinstance(fit_convention, MEGAlibRelativeY) and response_convention != 'RelativeY') or
            (isinstance(fit_convention, MEGAlibRelativeZ) and response_convention != 'RelativeZ')):
            raise RuntimeError("If performing fit in spacecraft frame, fit convention must match convention of response.")

        # if not type(data) == list:
        #     self._data = [data]
        # else:
        #     self._data = data

        self.SHOW_PLOTS = show_plots

        self._ori = sc_orientation

        self._convention = fit_convention

        self._response_convention = response_convention

        self._response_file = response_file

        self._response = FullDetectorResponse.open(response_file, pa_convention=self._response_convention)

        self._source_vector = source_vector

        self._spectrum = source_spectrum

        # Configure the ASAD binning before any ASADs or diagnostic plots
        # are created.  ``N`` edges define ``N - 1`` bins.
        if asad_bin_edges is None:
            self.asad_bin_edges = None
            self._nbins = int(self._response.axes['Pol'].nbins)
            self._asad_bins = self._nbins
            self._asad_bin_edges_rad = np.linspace(
                -np.pi, np.pi, self._nbins + 1
            )
            print(
                f'Using default ASAD binning: {self._nbins} bins '
                f'({self._nbins + 1} edges)'
            )
        else:
            edges = Angle(asad_bin_edges)

            if edges.isscalar or edges.ndim != 1:
                raise ValueError(
                    'asad_bin_edges must be a one-dimensional array of angles'
                )
            if edges.size < 2:
                raise ValueError(
                    'asad_bin_edges must contain at least two edges'
                )

            edges_rad = np.asarray(edges.to_value(u.rad), dtype=float)
            if not np.all(np.isfinite(edges_rad)):
                raise ValueError(
                    'asad_bin_edges must contain only finite values'
                )
            if not np.all(np.diff(edges_rad) > 0):
                raise ValueError(
                    'asad_bin_edges must be strictly increasing'
                )

            self.asad_bin_edges = Angle(edges_rad, unit=u.rad)
            self._asad_bins = self.asad_bin_edges
            self._asad_bin_edges_rad = edges_rad
            self._nbins = edges_rad.size - 1

            print(
                f'Using custom ASAD binning: {self._nbins} bins '
                f'({edges_rad.size} edges)'
            )
            print(
                'ASAD bin edges [deg]:',
                self.asad_bin_edges.to_value(u.deg),
            )

        self._reference_vector = self._convention.get_basis(source_vector)[0]

        self._expectation, self._azimuthal_angle_bins = self.convolve_spectrum(source_spectrum)

        self._energy_range = [min(self._response.axes['Em'].edges.value), max(self._response.axes['Em'].edges.value)]
        #print the energy range considered due to responses:
        print(f'Energy range considered (by responses design): {self._energy_range[0]} - {self._energy_range[1]} keV')

        # do a data cut before anything else! actually this should come as a separate routine: data selection and response
        # prep shold be done before analyzing the data
        if not type(data) == list:
            iii = np.where((data['Energies'] >= self._energy_range[0]) & (data['Energies'] <= self._energy_range[1]))
            self._data = [{key: data[key][iii] for key in data.keys()}]
        else:
            data_ecut_list = []
            for dlist in data:
                iii = np.where((dlist['Energies'] >= self._energy_range[0]) & (dlist['Energies'] <= self._energy_range[1]))
                data_ecut = {key: dlist[key][iii] for key in dlist.keys()}
                data_ecut_list.append(data_ecut)
            self._data = data_ecut_list

        self._exposure = sc_orientation.cumulative_livetime().to_value(u.second)

        self._data_duration = self.get_data_duration()

        self._data_counts = self.get_data_counts()

        self._data_azimuthal_angles = self.calculate_azimuthal_scattering_angles(self._data, show_plots=self.SHOW_PLOTS)

        self._background = background

        if self._background is not None:
            print('Background provided. Make sure there is enough statistics.')
            if not type(background) == list:
                iii = np.where((background['Energies'] >= self._energy_range[0]) & (background['Energies'] <= self._energy_range[1]))
                self._background = [{key: background[key][iii] for key in background.keys()}]
            else:
                background_ecut_list = []
                for bkg in background:
                    iii = np.where((bkg['Energies'] >= self._energy_range[0]) & (bkg['Energies'] <= self._energy_range[1]))
                    background_ecut = {key: bkg[key][iii] for key in bkg.keys()}
                    background_ecut_list.append(background_ecut)
                self._background = background_ecut_list

            self._background_azimuthal_angles = self.calculate_azimuthal_scattering_angles(self._background)
            self._background_duration = self.get_background_duration()
        else:
            print('No background provided. Will not subtract background from data.')
            self._background = None
            self._background_duration = 0
            self._background_azimuthal_angles = None

        self._mu100 = self.calculate_average_mu100(asad_bin_edges=self.asad_bin_edges, show_plots=False)

        self._mdp99 = self.calculate_mdp(modulation_factor=self._mu100['mu'])

    def get_data_counts(self):
        """
        Calculate the total counts in the data.

        Returns
        -------
        data_counts : int
            Total counts in the data
        """
        data_counts = 0
        for i in range(len(self._data)):
            if type(self._data[i]) == dict:
                data_counts += len(self._data[i]['TimeTags'])
            else:
                data_counts += self._data[i].binned_data.axes['Time'].nbins

        return data_counts

    def get_data_duration(self):
        """
        Calculate the total duration of the data.

        Returns
        -------
        data_duration : float
            Total duration of the data in seconds
        """
        for i in range(len(self._data)):

            if type(self._data[i]) == dict:

                if i == 0:
                    source_duration = np.max(self._data[i]['TimeTags']) - np.min(self._data[i]['TimeTags'])
                else:
                    source_duration += np.max(self._data[i]['TimeTags']) - np.min(self._data[i]['TimeTags'])

            else:

                if i == 0:
                    source_duration = (np.max(self._data[i].binned_data.axes['Time'].edges) - np.min(self._data[i].binned_data.axes['Time'].edges)).value
                else:
                    source_duration += (np.max(self._data[i].binned_data.axes['Time'].edges) - np.min(self._data[i].binned_data.axes['Time'].edges)).value

        return source_duration

    def get_background_duration(self):
        """
        Calculate the total duration of the data.
        Returns
        -------
        background_duration : float
            Total duration of the data in seconds
        """
        if self._background is None:
            background_duration = 0
        else:
            for i in range(len(self._background)):

                if type(self._background[i]) == dict:
                    if i == 0:
                        background_duration = np.max(self._background[i]['TimeTags']) - np.min(self._background[i]['TimeTags'])
                    else:
                        background_duration += np.max(self._background[i]['TimeTags']) - np.min(self._background[i]['TimeTags'])

                else:

                    if i == 0:
                        background_duration = (np.max(self._background[i].binned_data.axes['Time'].edges) - np.min(self._background[i].binned_data.axes['Time'].edges)).value
                    else:
                        background_duration += (np.max(self._background[i].binned_data.axes['Time'].edges) - np.min(self._background[i].binned_data.axes['Time'].edges)).value
        return background_duration

    def get_backscal(self):
        """
        Calculate the background scaling factor to match the source duration.

        Returns
        -------
        backscal : float
            Background scaling factor
        """
        if self._background_duration == 0:
            logger.warning('Background duration is zero, returning backscal = 0')
            backscal = None
        else:
            backscal = self._data_duration / self._background_duration

        return backscal

    def convolve_spectrum(self, spectrum):
        """
        Convolve source spectrum with response and calculate azimuthal scattering angle bins.

        Parameters
        ----------
        response_file : str or pathlib.Path
            Path to detector response
        sc_orientation : cosipy.spacecraftfile.SpacecraftFile.SpacecraftFile
            Spacecraft orientation

        Returns
        -------
        expectation : cosipy.response.PointSourceResponse.PointSourceResponse
            Expected counts in each bin of Compton data space
        azimuthal_angle_bins : list
            Centers of azimuthal scattering angle bins calculated from PsiChi bins in response
        """
        polarization_angle = PolarizationAngle(Angle(self._response.axes['Pol'].centers.angle.to_value(u.deg)[0] * u.deg), self._source_vector, convention=self._convention)
        polarization_level = 0
        if isinstance(self._convention.frame, SpacecraftFrame):
            print('>>> Convolving spectrum in spacecraft frame...')
            target_in_sc_frame = self._ori.get_target_in_sc_frame(target_name='source', target_coord=self._source_vector.transform_to('galactic'))
            dwell_time_map = self._ori.get_dwell_map(response=self._response_file, src_path=target_in_sc_frame, pa_convention=self._response_convention)
            psr = self._response.get_point_source_response(exposure_map=dwell_time_map, coord=self._source_vector.transform_to('galactic'))
            expectation = psr.get_expectation(spectrum, LinearPolarization(polarization_level * 100., polarization_angle.angle.deg))

            azimuthal_angle_bins = []

            for i in range(expectation.axes['PsiChi'].nbins):
                psichi = SkyCoord(lat=(np.pi/2) - expectation.axes['PsiChi'].pix2ang(i)[0], lon=expectation.axes['PsiChi'].pix2ang(i)[1], unit=u.rad, frame=self._convention.frame)
                azimuthal_angle = PolarizationAngle.from_scattering_direction(psichi, self._source_vector, self._convention)
                azimuthal_angle_bins.append(azimuthal_angle.angle)

        else:
            print('>>> Convolving spectrum in ICRS frame...')
            scatt_map = self._ori.get_scatt_map(nside=self._response.nside*2, target_coord=self._source_vector)
            # scatt_map = self._ori.get_scatt_map(nside=self._response.nside*2, target_coord=self._source_vector, coordsys='galactic')
            psr = self._response.get_point_source_response(coord=self._source_vector, scatt_map=scatt_map)
            expectation = psr.get_expectation(spectrum, LinearPolarization(polarization_level * 100., polarization_angle.angle.deg))

            azimuthal_angle_bins = []

            for i in range(expectation.axes['PsiChi'].nbins):
                psichi = expectation.axes['PsiChi'].pix2skycoord(i).transform_to('icrs')
                azimuthal_angle = PolarizationAngle.from_scattering_direction(psichi, self._source_vector, self._convention)
                azimuthal_angle_bins.append(azimuthal_angle.angle)

        return expectation, azimuthal_angle_bins

    def _angles_from_skycoords(self, scattering_directions):
        """Return vectorized signed scattering angles for SkyCoord arrays."""
        scattering = np.asarray(
            scattering_directions.cartesian.xyz.value, dtype=float
        ).T
        source = np.asarray(
            self._source_vector.cartesian.xyz.value, dtype=float
        ).reshape(3)
        reference = np.asarray(
            self._reference_vector.cartesian.xyz.value, dtype=float
        ).reshape(3)

        source /= np.linalg.norm(source)
        reference -= np.dot(reference, source) * source
        reference_norm = np.linalg.norm(reference)
        if reference_norm == 0:
            raise ValueError("The reference vector is parallel to the source vector")
        reference /= reference_norm

        projection = scattering - (scattering @ source)[:, None] * source
        projection_norm = np.linalg.norm(projection, axis=1)
        valid = projection_norm > np.finfo(float).eps

        projection_unit = np.full_like(projection, np.nan)
        projection_unit[valid] = projection[valid] / projection_norm[valid, None]

        x = np.clip(projection_unit @ reference, -1.0, 1.0)
        y = np.einsum("i,ni->n", source, np.cross(projection_unit, reference))
        return Angle(np.arctan2(y, x), unit=u.rad)

    def calculate_azimuthal_scattering_angles(self, unbinned_data, show_plots=False):
        """Calculate all event scattering angles without per-event Python loops."""
        if isinstance(unbinned_data, dict):
            datasets = [unbinned_data]
        elif isinstance(unbinned_data, list):
            datasets = unbinned_data
        else:
            raise TypeError("unbinned_data must be a dict or a list of dicts")

        if not datasets:
            return Angle(np.array([], dtype=float), unit=u.rad)
        if not all(isinstance(dataset, dict) for dataset in datasets):
            raise TypeError("Every unbinned dataset must be a dictionary")

        if isinstance(self._convention.frame, SpacecraftFrame):
            psi = np.concatenate([
                np.asarray(dataset["Psi local"], dtype=float).reshape(-1)
                for dataset in datasets
            ])
            chi = np.concatenate([
                np.asarray(dataset["Chi local"], dtype=float).reshape(-1)
                for dataset in datasets
            ])
            if psi.size != chi.size:
                raise ValueError("Psi local and Chi local must have the same length")
            azimuthal_angles = calculate_azimuthal_scattering_angle(
                psi, chi, self._source_vector, self._reference_vector
            )
        else:
            latitude = np.concatenate([
                np.asarray(dataset["Psi galactic"], dtype=float).reshape(-1)
                for dataset in datasets
            ])
            longitude = np.concatenate([
                np.asarray(dataset["Chi galactic"], dtype=float).reshape(-1)
                for dataset in datasets
            ])
            if latitude.size != longitude.size:
                raise ValueError("Psi galactic and Chi galactic must have the same length")

            scattering_directions = SkyCoord(
                l=longitude,
                b=latitude,
                frame="galactic",
                unit=u.deg,
            ).transform_to("icrs")
            azimuthal_angles = self._angles_from_skycoords(scattering_directions)

        if show_plots:
            values = azimuthal_angles.to_value(u.rad)
            plt.figure()
            plt.title("Azimuthal scattering angles")
            plt.hist(values, bins=50, alpha=0.5, label="Data fine binning")
            plt.hist(
                values,
                bins=self._asad_bin_edges_rad,
                alpha=0.5,
                histtype="step",
                linewidth=2,
                label="Response binning",
            )
            plt.xlabel("Azimuthal angle (radians)")
            plt.ylabel("Counts")
            plt.legend()
            plt.show()

        return azimuthal_angles

    def calculate_average_mu100(self, asad_bin_edges=None, show_plots=False):
        """
        Calculate the modulation (mu) of an 100% polarized source.

        Parameters
        ----------
        asad_bin_edges : array-like, optional
            Bin edges for the ASAD. If None, default binning is used.
        show_plots : bool, optional
            Option to show plots. Default is False

        Returns
        -------
        mu_100 : dict
            Modulation of 100% polarized source and uncertainty of constant function fit to modulation in all polarization angle bins
        """

        # The binning was validated and stored during initialization.
        # Keep this optional argument for backward compatibility, but do not
        # overwrite ``self._nbins`` with an array of edges.
        if asad_bin_edges is not None:
            requested_edges = Angle(asad_bin_edges).to_value(u.rad)
            if not np.array_equal(
                np.asarray(requested_edges, dtype=float),
                self._asad_bin_edges_rad,
            ):
                raise ValueError(
                    'asad_bin_edges differs from the binning configured '
                    'during initialization'
                )

        print(
            f'Calculating mu100 with {self._nbins} ASAD bins '
            f'({self._nbins + 1} edges)'
        )
        print('Creating the 100% polarized ASADs (this may take a minute...)')
        polarized_asads = create_polarized_asads(
            self._spectrum,
            self._source_vector,
            self._ori,
            self._response,
            self._convention,
            self._response_file,
            self._response_convention,
            bins=self._asad_bins,
        )
        print('Creating the unpolarized ASAD...')
        unpolarized_asad = create_unpolarized_asad(
            self._spectrum,
            self._source_vector,
            self._ori,
            self._response,
            self._convention,
            self._response_file,
            self._response_convention,
            bins=self._asad_bins,
        )
        mu_100_list = []
        mu_100_uncertainties = []

        for i in range(self._response.axes['Pol'].nbins):
            logger.info('Polarization angle bin: ' + str(self._response.axes['Pol'].edges.angle.to_value(u.deg)[i]) + ' to ' + str(self._response.axes['Pol'].edges.angle.to_value(u.deg)[i+1]) + ' deg')
            asad_corrected = polarized_asads[i] / np.sum(polarized_asads[i]) / unpolarized_asad * np.sum(unpolarized_asad)
            mu, mu_err = get_modulation(asad_corrected.axis.centers.value, asad_corrected.full_contents,
                                        title='Modulation PA bin %i'%i, show=show_plots)
            mu_100_list.append(mu)
            mu_100_uncertainties.append(mu_err)

        popt, pcov = curve_fit(constant, self._response.axes['Pol'].centers.angle.to_value(u.deg), mu_100_list,
                               sigma=mu_100_uncertainties, p0=np.mean(mu_100_list), absolute_sigma=True)
        mu_100 = {'mu': popt[0], 'uncertainty': pcov[0][0]}

        if show_plots == True:
            plt.figure()
            plt.scatter(self._response.axes['Pol'].centers.angle.to_value(u.deg), mu_100_list)
            plt.errorbar(self._response.axes['Pol'].centers.angle.to_value(u.deg), mu_100_list,
                         yerr=mu_100_uncertainties, linewidth=0, elinewidth=1)
            plt.plot([0, 175], [mu_100['mu'], mu_100['mu']])
            plt.xlabel('Polarization Angle (degrees)')
            plt.ylabel('mu_100')
            plt.show()

        return mu_100

    def compute_data_pseudo_stokes(self, show_plots=False):
        """Vectorized pseudo-Stokes parameters for source data."""
        angles = Angle(self._data_azimuthal_angles).to_value(u.rad)
        shifted = angles - np.pi / 2.0
        qs = np.asarray(stokes_q(shifted), dtype=float)
        us = np.asarray(stokes_u(shifted), dtype=float)

        if show_plots:
            plt.figure()
            plt.title(f"Source Stokes parameters ({qs.size} events)")
            plt.hist(qs, bins=50, alpha=0.5, label=r"$q_s$")
            plt.hist(us, bins=50, alpha=0.5, label=r"$u_s$")
            plt.xlabel("Pseudo Stokes parameter")
            plt.legend()
            plt.show()
        return qs, us

    def compute_background_pseudo_stokes(self, show_plots=False):
        """Vectorized pseudo-Stokes parameters for background data."""
        if self._background_azimuthal_angles is None:
            logger.warning("No background data provided; returning empty arrays.")
            return np.array([], dtype=float), np.array([], dtype=float)

        angles = Angle(self._background_azimuthal_angles).to_value(u.rad)
        shifted = angles - np.pi / 2.0
        qs = np.asarray(stokes_q(shifted), dtype=float)
        us = np.asarray(stokes_u(shifted), dtype=float)

        if show_plots:
            plt.figure()
            plt.title(f"Background Stokes parameters ({qs.size} events)")
            plt.hist(qs, bins=50, alpha=0.5, label=r"$q_b$")
            plt.hist(us, bins=50, alpha=0.5, label=r"$u_b$")
            plt.xlabel("Pseudo Stokes parameter")
            plt.legend()
            plt.show()
        return qs, us

    def calculate_mdp(self, modulation_factor):
        """Calculate the 99% minimum detectable polarization consistently.

        The source-region data contain source + background.  For an
        independently measured background sample scaled by
        ``alpha = T_data / T_background``, the variance of a
        background-subtracted Stokes sum is proportional to
        ``N_on + alpha**2 * N_off``.
        """
        if not np.isfinite(modulation_factor) or modulation_factor <= 0:
            raise ValueError("modulation_factor must be positive and finite")

        n_on = float(sum(len(dataset["TimeTags"]) for dataset in self._data))
        if n_on <= 0:
            raise ValueError("The source-region data contain no events")

        if self._background is None:
            n_source = n_on
            variance_counts = n_on
        else:
            n_off = float(
                sum(len(dataset["TimeTags"]) for dataset in self._background)
            )
            alpha = self.get_backscal()
            if alpha is None or not np.isfinite(alpha) or alpha <= 0:
                raise ValueError("A positive finite BACKSCAL is required")

            n_source = n_on - alpha * n_off
            variance_counts = n_on + alpha**2 * n_off

            if n_source <= 0:
                raise ValueError(
                    "The background-subtracted source count is not positive: "
                    f"N_on={n_on}, alpha={alpha:.6g}, N_off={n_off}, "
                    f"N_source={n_source:.6g}."
                )

        mdp = 4.29 * np.sqrt(variance_counts) / (
            modulation_factor * n_source
        )
        logger.info("Minimum detectable polarization (MDP99): %.6f", mdp)
        return float(mdp)

    def calculate_polarization(
        self,
        qs,
        us,
        mu,
        bkg_qs=None,
        bkg_us=None,
        show_plots=False,
        ref_qu=(None, None),
        ref_pdpa=(None, None),
        ref_label=None,
        mdp=None,
    ):
        """Calculate background-subtracted PD and PA with propagated errors.

        ``qs`` and ``us`` are the event-level pseudo-Stokes values from the
        on-source region.  The background arrays are an independent off-source
        sample.  Their Stokes sums are scaled by ``alpha`` before subtraction.

        The covariance of the net Stokes sums is estimated directly from the
        event-level second moments.  This avoids applying a source-only error
        formula to background-subtracted data.
        """
        qs = np.asarray(qs, dtype=float).reshape(-1)
        us = np.asarray(us, dtype=float).reshape(-1)

        if qs.size != us.size:
            raise ValueError("qs and us must contain the same number of events")
        if qs.size < 2:
            raise ValueError("At least two source-region events are required")
        if not np.all(np.isfinite(qs)) or not np.all(np.isfinite(us)):
            raise ValueError("qs and us must contain only finite values")
        if not np.isfinite(mu) or mu <= 0:
            raise ValueError("mu must be positive and finite")

        n_on = float(qs.size)
        q_on = float(np.sum(qs))
        u_on = float(np.sum(us))

        has_background = bkg_qs is not None or bkg_us is not None
        if has_background and (bkg_qs is None or bkg_us is None):
            raise ValueError("Provide both bkg_qs and bkg_us, or neither")

        if has_background:
            bkg_qs = np.asarray(bkg_qs, dtype=float).reshape(-1)
            bkg_us = np.asarray(bkg_us, dtype=float).reshape(-1)

            if bkg_qs.size != bkg_us.size:
                raise ValueError(
                    "bkg_qs and bkg_us must contain the same number of events"
                )
            if bkg_qs.size < 2:
                raise ValueError("At least two background events are required")
            if not np.all(np.isfinite(bkg_qs)) or not np.all(np.isfinite(bkg_us)):
                raise ValueError("Background Stokes arrays must be finite")

            alpha = self.get_backscal()
            if alpha is None or not np.isfinite(alpha) or alpha <= 0:
                raise ValueError("A positive finite BACKSCAL is required")

            n_off = float(bkg_qs.size)
            q_off = float(np.sum(bkg_qs))
            u_off = float(np.sum(bkg_us))
        else:
            alpha = 0.0
            n_off = 0.0
            q_off = 0.0
            u_off = 0.0
            bkg_qs = np.empty(0, dtype=float)
            bkg_us = np.empty(0, dtype=float)

        # Net source intensity and net pseudo-Stokes sums.
        n_source = n_on - alpha * n_off
        q_net = q_on - alpha * q_off
        u_net = u_on - alpha * u_off

        if n_source <= 1:
            raise ValueError(
                "The background-subtracted source count must exceed one: "
                f"N_on={n_on}, alpha={alpha:.6g}, N_off={n_off}, "
                f"N_source={n_source:.6g}."
            )

        self.QN = q_net / (mu * n_source)
        self.UN = u_net / (mu * n_source)

        pd = float(np.hypot(self.QN, self.UN))
        pa = float(np.mod(0.5 * np.arctan2(self.UN, self.QN), np.pi))

        # Estimate covariance of the net Stokes sums from event-level moments.
        # For an independent off-source sample:
        # Cov(net) = Cov(on sum) + alpha^2 Cov(off sum).
        on_matrix = np.column_stack((qs, us))
        cov_on_event = np.cov(on_matrix, rowvar=False, ddof=1)
        cov_on_sum = n_on * cov_on_event

        if has_background:
            off_matrix = np.column_stack((bkg_qs, bkg_us))
            cov_off_event = np.cov(off_matrix, rowvar=False, ddof=1)
            cov_off_sum = n_off * cov_off_event
        else:
            cov_off_sum = np.zeros((2, 2), dtype=float)

        cov_net_sum = cov_on_sum + alpha**2 * cov_off_sum
        cov_normalized = cov_net_sum / (mu * n_source) ** 2

        var_qn = float(max(cov_normalized[0, 0], 0.0))
        var_un = float(max(cov_normalized[1, 1], 0.0))
        cov_qu = float(cov_normalized[0, 1])

        sigma_qn = np.sqrt(var_qn)
        sigma_un = np.sqrt(var_un)

        # Delta-method propagation to radial PD and angular PA.
        if pd > np.finfo(float).eps:
            grad_pd = np.array([self.QN / pd, self.UN / pd])
            var_pd = float(grad_pd @ cov_normalized @ grad_pd)

            denominator = self.QN**2 + self.UN**2
            grad_pa = np.array(
                [-0.5 * self.UN / denominator,
                  0.5 * self.QN / denominator]
            )
            var_pa = float(grad_pa @ cov_normalized @ grad_pa)

            sigma_pd = np.sqrt(max(var_pd, 0.0))
            sigma_pa_rad = np.sqrt(max(var_pa, 0.0))
        else:
            # PA is undefined at zero polarization.  Use a conservative radial
            # scale for PD and report an infinite PA uncertainty.
            sigma_pd = np.sqrt(max(var_qn + var_un, 0.0))
            sigma_pa_rad = np.inf

        sigma_pa_deg = np.degrees(sigma_pa_rad)

        # A consistent MDP based on the same on/off counts and scaling.
        variance_counts = n_on + alpha**2 * n_off
        mdp99 = 4.29 * np.sqrt(variance_counts) / (mu * n_source)
        self._mdp99 = float(mdp99)

        print(f"N_on                 = {n_on:.0f}")
        print(f"N_off                = {n_off:.0f}")
        print(f"BACKSCAL              = {alpha:.8g}")
        print(f"N_background_scaled  = {alpha * n_off:.6g}")
        print(f"N_source_net         = {n_source:.6g}")
        print(f"mu100                 = {mu:.8g}")
        print(f"Q/I                   = {self.QN:.8g}")
        print(f"U/I                   = {self.UN:.8g}")
        print(f"PD                    = {100.0 * pd:.3f} +/- {100.0 * sigma_pd:.3f} %")
        print(f"PA                    = {np.degrees(pa):.3f} +/- {sigma_pa_deg:.3f} deg")
        print(f"MDP99                 = {100.0 * mdp99:.3f} %")

        if show_plots:
            fig, ax = plt.subplots(figsize=(6.7, 6.4))
            polar_chart_backbone(ax)

            if ref_qu[0] is not None:
                ax.plot(ref_qu[0], ref_qu[1], "x", markersize=20)
                ax.annotate(
                    ref_label,
                    (ref_qu[0], ref_qu[1]),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=12,
                )

            if ref_pdpa[0] is not None:
                ref_q, ref_u = rotate_points_to_x_axis(
                    ref_pdpa[0], np.radians(ref_pdpa[1])
                )
                ax.plot(ref_q, ref_u, "x", markersize=20)
                ax.annotate(
                    ref_label,
                    (ref_q, ref_u),
                    textcoords="offset points",
                    xytext=(0, 10),
                    ha="center",
                    fontsize=12,
                )

            mdp_to_plot = self._mdp99 if mdp is None else float(mdp)
            mdp_circle = plt.Circle(
                (0, 0),
                radius=mdp_to_plot,
                facecolor="none",
                linestyle="--",
                linewidth=1,
                label=rf"MDP$_{{99}}$ = {100.0 * mdp_to_plot:.2f} %",
            )
            ax.add_artist(mdp_circle)

            if has_background:
                qn_bkg = q_off / (mu * n_off)
                un_bkg = u_off / (mu * n_off)
                ax.plot(
                    qn_bkg,
                    un_bkg,
                    "o",
                    markersize=5,
                    label="Background sample",
                )
                label_data = (
                    "Measured (background subtracted)\n"
                    f"PD = ({100.0 * pd:.1f} +/- {100.0 * sigma_pd:.1f})%\n"
                    f"PA = ({np.degrees(pa):.1f} +/- {sigma_pa_deg:.1f}) deg"
                )
            else:
                label_data = (
                    f"PD = ({100.0 * pd:.1f} +/- {100.0 * sigma_pd:.1f})%\n"
                    f"PA = ({np.degrees(pa):.1f} +/- {sigma_pa_deg:.1f}) deg"
                )

            ax.plot(self.QN, self.UN, "o", markersize=5, label=label_data)

            # Draw the full covariance ellipse rather than circular errors.
            eigenvalues, eigenvectors = np.linalg.eigh(cov_normalized)
            eigenvalues = np.maximum(eigenvalues, 0.0)
            order = np.argsort(eigenvalues)[::-1]
            eigenvalues = eigenvalues[order]
            eigenvectors = eigenvectors[:, order]
            ellipse_angle = np.degrees(
                np.arctan2(eigenvectors[1, 0], eigenvectors[0, 0])
            )

            from matplotlib.patches import Ellipse
            for nsigma in (1, 2, 3):
                ellipse = Ellipse(
                    xy=(self.QN, self.UN),
                    width=2 * nsigma * np.sqrt(eigenvalues[0]),
                    height=2 * nsigma * np.sqrt(eigenvalues[1]),
                    angle=ellipse_angle,
                    fill=False,
                    linewidth=1,
                )
                ax.add_patch(ellipse)

            ax.set_xlim(-1, 1)
            ax.set_ylim(-1, 1)
            ax.set_xlabel("Q/I")
            ax.set_ylabel("U/I")
            ax.legend(fontsize=11)
            fig.tight_layout()
            plt.show()

        polarization_angle = Angle(np.degrees(pa), unit=u.deg)
        polarization_angle = PolarizationAngle(
            polarization_angle,
            self._source_vector,
            convention=self._convention,
        ).transform_to(IAUPolarizationConvention())

        return {
            "fraction": pd,
            "angle": polarization_angle,
            "fraction_uncertainty": float(sigma_pd),
            "angle_uncertainty": Angle(sigma_pa_deg, unit=u.deg),
            "QN": self.QN,
            "UN": self.UN,
            "QN_ERR": float(sigma_qn),
            "UN_ERR": float(sigma_un),
            "QN_UN_COV": cov_qu,
            "MDP99": float(mdp99),
            "N_ON": n_on,
            "N_OFF": n_off,
            "BACKSCAL": float(alpha),
            "N_SOURCE_NET": float(n_source),
        }


if __name__ == "__main__":

    print('Just some tests here...')

    pass

# MAB ////////////////////////////////////////////////////////////////////////////////////////////


