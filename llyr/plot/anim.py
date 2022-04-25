import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from .._utils import hsl2rgb

from ..base import Base


class anim(Base):
    def plot(
        self,
        dset: str = "m",
        f: float = 9,
        z: int = 0,
        periods: int = 1,
        save_path: str = None,
        repeat: int = 1,
        figax=None,
    ):
        arr = self.llyr.calc.anim(dset, f, periods=periods)[:, z]
        arr = np.tile(arr, (1, repeat, repeat, 1))
        arr = np.ma.masked_equal(arr, 0)
        u, v, w = arr[..., 0], arr[..., 1], arr[..., 2]
        alphas = -np.abs(w) + 1
        hsl = np.ones((u.shape[0], u.shape[1], u.shape[2], 3))
        hsl[..., 0] = np.angle(u + 1j * v) / np.pi / 2  # normalization
        hsl[..., 1] = np.sqrt(u**2 + v**2 + w**2)
        hsl[..., 2] = (w + 1) / 2
        rgb = hsl2rgb(hsl)
        stepx = max(int(u.shape[2] / 60), 1)
        stepy = max(int(u.shape[1] / 60), 1)
        scale = 1 / max(stepx, stepy)
        x, y = np.meshgrid(
            np.arange(0, u.shape[2], stepx) * self.llyr.dx * 1e9,
            np.arange(0, u.shape[1], stepy) * self.llyr.dy * 1e9,
        )
        antidots = np.ma.masked_not_equal(self.llyr["m"][0, 0, :, :, 2], 0)
        antidots = np.tile(antidots, (repeat, repeat))
        extent = [
            0,
            arr.shape[2] * self.llyr.dx * 1e9,
            0,
            arr.shape[1] * self.llyr.dy * 1e9,
        ]
        t = 0
        if figax is None:
            fig, ax = plt.subplots(1, 1, figsize=(3, 3), dpi=200)
        else:
            fig, ax = figax
        Q = ax.quiver(
            x,
            y,
            u[t, ::stepy, ::stepx],
            v[t, ::stepy, ::stepx],
            alpha=alphas[t, ::stepy, ::stepx],
            angles="xy",
            scale_units="xy",
            scale=scale,
        )
        ax.imshow(
            rgb[t],
            interpolation="None",
            origin="lower",
            cmap="hsv",
            vmin=-np.pi,
            vmax=np.pi,
            extent=extent,
        )
        ax.imshow(
            antidots, interpolation="None", origin="lower", cmap="Set1_r", extent=extent
        )
        ax.set(xlabel="x (nm)", ylabel="y (nm)", title=f"{f:.2f} GHz")
        fig.tight_layout()

        def run(t):
            ax.get_images()[0].set_data(rgb[t])
            Q.set_UVC(u[t, ::stepy, ::stepx], v[t, ::stepy, ::stepx])
            Q.set_alpha(alphas[t, ::stepy, ::stepx])
            return ax

        ani = FuncAnimation(
            fig, run, interval=1, frames=np.arange(1, arr.shape[0], dtype="int")
        )
        # plt.show()
        # return ani
        if save_path is None:
            anim_save_path = f"{self.llyr.abs_path}_{f}.gif"
        else:
            anim_save_path = save_path
        ani.save(
            anim_save_path,
            writer="ffmpeg",
            fps=25,
            dpi=300,
            # extra_args=["-vcodec", "h264", "-pix_fmt", "yuv420p"],
        )
        # print(f"Saved at: {anim_save_path}")
        plt.close()
