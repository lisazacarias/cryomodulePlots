import sys
import warnings
from os import path
from typing import Optional

from lcls_tools.common.frontend.plotting.util import TimePlotUpdater, TimePlotParams
from lcls_tools.superconducting.sc_linac_utils import ALL_CRYOMODULES
from pydm import Display

import plot_utils
from plot_linac import Decarad, PLOT_CRYO_MACHINE, PlotCryomodule

warnings.filterwarnings("ignore", category=RuntimeWarning)


class CryomodulePlots(Display):
    
    def ui_filename(self):
        return 'cryomodule_signals.ui'
    
    def __init__(self, parent=None, args=None):
        super().__init__(parent=parent, args=args)
        
        self.pathHere = path.dirname(sys.modules[self.__module__].__file__)
        
        self.current_cm: Optional[PlotCryomodule] = None
        self.ui.cryo_combobox.addItems(["None"] + ALL_CRYOMODULES)
        self.ui.cryo_combobox.currentIndexChanged.connect(self.update_cryomodule)
        self.ui.decarad_combobox.currentIndexChanged.connect(self.update_decarad)
        self.time_plot_updater: TimePlotUpdater = None
        self.setup_plots()
        
        self.decarads = {"1": Decarad(1), "2": Decarad(2)}
        
        self.decarad = None
        
        self.ui.timespan_spinbox.editingFinished.connect(self.update_plot_timespan)
    
    def update_plot_timespan(self):
        self.time_plot_updater.updateTimespans(self.ui.timespan_spinbox.value())
    
    def update_cryomodule(self):
        try:
            self.current_cm = PLOT_CRYO_MACHINE.cryomodules[self.ui.cryo_combobox.currentText()]
            
            timeplot_update_map = {plot_utils.STEPPERTEMP_PLOT_KEY: self.current_cm.stepper_temp_pvs,
                                   plot_utils.HOMDS_PLOT_KEY      : self.current_cm.hom_ds_pvs,
                                   plot_utils.HOMUS_PLOT_KEY      : self.current_cm.hom_us_pvs,
                                   plot_utils.CPLRTOP_PLOT_KEY    : self.current_cm.coupler_top_pvs,
                                   plot_utils.CPLRBOT_PLOT_KEY    : self.current_cm.coupler_bot_pvs,
                                   plot_utils.CMVACUUM_PLOT_KEY   : self.current_cm.vacuumPlotPairs,
                                   plot_utils.CRYOSIGNALS_PLOT_KEY: self.current_cm.cryo_signal_PVs,
                                   plot_utils.AMP_PLOT_KEY        : self.current_cm.amp_pvs}
            
            self.time_plot_updater.updatePlots(timeplot_update_map)
        except KeyError:
            self.time_plot_updater.clear_plots()
    
    def setup_plots(self):
        time_plot_updater = {
            plot_utils.STEPPERTEMP_PLOT_KEY: TimePlotParams(plot=self.ui.plot_steppertemps,
                                                            formLayout=self.ui.stepper_form),
            plot_utils.HOMUS_PLOT_KEY      : TimePlotParams(plot=self.ui.plot_homus_temp,
                                                            formLayout=self.ui.up_hom_form),
            plot_utils.HOMDS_PLOT_KEY      : TimePlotParams(plot=self.ui.plot_homds_temp,
                                                            formLayout=self.ui.down_hom_form),
            plot_utils.CPLRTOP_PLOT_KEY    : TimePlotParams(plot=self.ui.plot_couplertop_temp,
                                                            formLayout=self.ui.coup_top_form),
            plot_utils.CPLRBOT_PLOT_KEY    : TimePlotParams(plot=self.ui.plot_couplerbot_temp,
                                                            formLayout=self.ui.coup_bot_hom),
            plot_utils.CMVACUUM_PLOT_KEY   : TimePlotParams(plot=self.ui.plot_cmvacuum,
                                                            formLayout=self.ui.vacuum_form),
            plot_utils.CRYOSIGNALS_PLOT_KEY: TimePlotParams(plot=self.ui.plot_cryosignals,
                                                            formLayout=self.ui.cryo_form),
            plot_utils.DECARAD_PLOT_KEY    : TimePlotParams(plot=self.ui.plot_decarad,
                                                            formLayout=self.ui.decarad_form),
            plot_utils.AMP_PLOT_KEY        : TimePlotParams(plot=self.ui.plot_amps,
                                                            formLayout=self.ui.amp_form)
        }
        self.time_plot_updater = TimePlotUpdater(time_plot_updater)
    
    def getPath(self, fileName):
        return path.join(self.pathHere, fileName)
    
    def update_decarad(self):
        try:
            self.decarad = self.decarads[self.ui.decarad_combobox.currentText()]
            timeplot_update_map = {plot_utils.DECARAD_PLOT_KEY: self.decarad.head_pvs}
            self.time_plot_updater.updatePlots(timeplot_update_map)
        
        except KeyError:
            self.time_plot_updater.clear_plot(plot_utils.DECARAD_PLOT_KEY)
