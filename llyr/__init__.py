import os
from pathlib import Path
import shutil

import numpy as np
import zarr
from .plot import Plot
from .calc import Calc

from ._utils import (
    h5_to_zarr,
    load_ovf,
    merge_table,
    get_ovf_parms,
    out_to_zarr,
    hsl2rgb,
    MidpointNormalize,
    save_ovf,
    get_cmaps,
    add_radial_phase_colormap,
    fix_bg,
    make_cmap,
)
from ._iplot import iplotp
from ._iplot2 import iplotp2
from .ip import ipp


__all__ = [
    "h5_to_zarr",
    "load_ovf",
    "merge_table",
    "get_ovf_parms",
    "out_to_zarr",
    "hsl2rgb",
    "iplot",
    "MidpointNormalize",
    "save_ovf",
    "get_cmaps",
    "fix_bg",
    "iplot",
    "iplot2",
    "add_radial_phase_colormap",
    "op",
    "ip",
    "make_cmap",
]


def iplot(*args, **kwargs):
    return iplotp(op, *args, **kwargs)


def iplot2(*args, **kwargs):
    return iplotp2(op, *args, **kwargs)


def ip(*args, **kwargs):
    return ipp(op, *args, **kwargs)


def op(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"Path Not Found : '{path}'")
    if "ssh://" in path:
        return Group(zarr.storage.FSStore(path))
    else:
        return Group(zarr.storage.DirectoryStore(path))


class Group(zarr.hierarchy.Group):
    def __init__(self, store) -> None:
        zarr.hierarchy.Group.__init__(self, store)
        self.abs_path = Path(store.path).absolute()
        self.sim_name = self.abs_path.name.replace(self.abs_path.suffix, "")
        self.plot = Plot(self)
        self.calc = Calc(self)
        self.reload()

    def __repr__(self) -> str:
        return f"Llyr('{self.sim_name}')"

    def __str__(self) -> str:
        return f"Llyr('{self.sim_name}')"

    def reload(self):
        self._update_class_dict()

    def _update_class_dict(self):
        for k, v in self.attrs.items():
            self.__dict__[k] = v

    def rm(self, dset: str):
        shutil.rmtree(f"{self.abs_path}/{dset}", ignore_errors=True)

    def mkdir(self, name: str):
        os.makedirs(f"{self.abs_path}/{name}", exist_ok=True)

    @property
    def pp(self):
        return self.tree(expand=True)

    @property
    def p(self):
        print(self.tree())

    def c_to_comp(self, c):
        return ["mx", "my", "mz"][c]

    def comp_to_c(self, c):
        return {"mx": 0, "my": 1, "mz": 2}[c]

    def get_mode(self, dset: str, f: float, c=None):
        if f"modes/{dset}/arr" not in self:
            print("Calculating modes ...")
            self.calc.modes(dset)
        fi = int((np.abs(self[f"modes/{dset}/freqs"][:] - f)).argmin())
        arr = self[f"modes/{dset}/arr"][fi]
        if c is None:
            return arr
        else:
            return arr[..., c]

    def get_fft(self, c, xmin: int = 0, normalize=True, force=False):
        if "fft/m" not in self or force:
            print("Calculating modes ...")
        freqs = self.fft.m.freqs[xmin:]
        fft = self.fft.m.max[xmin:, c]
        if normalize:
            fft /= fft.max()
        return freqs, fft

    def check_path(self, dset: str, force: bool = False):
        if dset in self:
            if force:
                self.rm(dset)
            else:
                raise NameError(
                    f"The dataset:'{dset}' already exists, you can use 'force=True'"
                )
