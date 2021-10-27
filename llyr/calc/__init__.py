from .disp import disp
from .fft_tb import fft_tb
from .fft import fft
from .mode import mode
from .sk_number import sk_number
from .peaks import peaks
from .fminmax import fminmax
from .sin_anim import sin_anim


class Calc:
    def __init__(self, llyr):
        self.disp = disp(llyr).calc
        self.fft_tb = fft_tb(llyr).calc
        self.fft = fft(llyr).calc
        self.mode = mode(llyr).calc
        self.sk_number = sk_number(llyr).calc
        self.peaks = peaks(llyr).calc
        self.fminmax = fminmax(llyr).calc
        self.sin_anim = sin_anim(llyr).calc
