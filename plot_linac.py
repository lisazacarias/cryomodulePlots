from typing import Dict, List, Tuple

from epics import caget
from lcls_tools.superconducting.sc_cavity import Cavity
from lcls_tools.superconducting.sc_cryomodule import Cryomodule
from lcls_tools.superconducting.sc_linac import Machine

from plot_utils import DECARAD_BACKGROUND_READING


class DecaradHead:
    def __init__(self, number, decarad):
        # type (int, Decarad) -> None
        
        if number not in range(1, 11):
            raise AttributeError("Decarad Head number need to be between 1 and 10")
        
        self.decarad = decarad
        self.number = number
        
        # Adds leading 0 to numbers with less than 2 digits
        self.pvPrefix = self.decarad.pvPrefix + "{:02d}:".format(self.number)
        
        self.doseRatePV: str = self.pvPrefix + "GAMMAAVE"
        self.decarad.head_pvs.append((self.doseRatePV, None))
        
        self.counter = 0
    
    @property
    def normalized_dose(self) -> float:
        return max(caget(self.doseRatePV) - DECARAD_BACKGROUND_READING, 0)


class Decarad:
    def __init__(self, number):
        # type: (int) -> None
        if number not in [1, 2]:
            raise AttributeError("Decarad needs to be 1 or 2")
        self.number = number
        self.pvPrefix = "RADM:SYS0:{num}00:".format(num=self.number)
        self.head_pvs: List[Tuple[str, str]] = []
        
        self.heads: Dict[int, DecaradHead] = {head: DecaradHead(number=head,
                                                                decarad=self)
                                              for head in range(1, 11)}
    
    @property
    def max_dose(self):
        return max([head.normalized_dose for head in self.heads.values()])


class PlotCavity(Cavity):
    
    def __init__(self, cavity_num, rack_object):
        super().__init__(cavity_num=cavity_num, rack_object=rack_object)
        
        self.coupler_top_pv = self.pvPrefix + "CPLRTEMP1"
        self.coupler_bot_pv = self.pvPrefix + "CPLRTEMP2"
        self.hom_us_pv = self.ctePrefix + "18:UH:TEMP"
        self.hom_ds_pv = self.ctePrefix + "20:DH:TEMP"
        self.vessel_top_pv = self.ctePrefix + "14:VT:TEMP"
        self.vessel_bot_pv = self.ctePrefix + "15:VB:TEMP"
        
        self.plot_pvs: List[str] = [(self.stepper_temp_pv, None),
                                    (self.coupler_top_pv, None),
                                    (self.coupler_bot_pv, None),
                                    (self.hom_ds_pv, None),
                                    (self.hom_us_pv, None),
                                    (self.vessel_top_pv, None),
                                    (self.vessel_bot_pv, None),
                                    (self.selAmplitudeActPV.pvname, None)]


class PlotCryomodule(Cryomodule):
    def __init__(self, cryo_name, linac_object):
        super().__init__(cryo_name=cryo_name, linac_object=linac_object)
        
        self.stepper_temp_pvs = []
        self.coupler_top_pvs = []
        self.coupler_bot_pvs = []
        self.hom_us_pvs = []
        self.hom_ds_pvs = []
        self.detune_pvs = []
        self.amp_pvs = []
        
        for cavity in self.cavities.values():
            self.stepper_temp_pvs.append((cavity.stepper_temp_pv, None))
            self.coupler_top_pvs.append((cavity.coupler_top_pv, None))
            self.coupler_bot_pvs.append((cavity.coupler_bot_pv, None))
            self.hom_us_pvs.append((cavity.hom_us_pv, None))
            self.hom_ds_pvs.append((cavity.hom_ds_pv, None))
            self.detune_pvs.append((cavity.detune_best_pv.pvname, None))
            self.amp_pvs.append((cavity.aact_pv.pvname, None))
        
        self.cryo_signal_PVs = [(self.ds_level_pv, "ds"),
                                (self.us_level_pv, "us"),
                                (self.ds_pressure_pv, "press"),
                                (self.jt_valve_readback_pv, "jt"),
                                (self.heater_readback_pv, "heat")]
        
        self.vacuumPlotPairs = [(pv.pvname, "x96")
                                for pv in self.linac.insulatingVacuumPVs]
        self.vacuumPlotPairs += [(pv.pvname, "!96") for pv in self.linac.beamlineVacuumPVs]
        self.vacuumPlotPairs += [(pv.pvname, "!96") for pv in self.couplerVacuumPVs]


PLOT_CRYO_MACHINE = Machine(cavity_class=PlotCavity, cryomodule_class=PlotCryomodule)
