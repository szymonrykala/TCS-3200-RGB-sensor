import tkinter as tk
from dataclasses import dataclass
from tkinter import ttk

BASE_PADDING = 10


@dataclass
class RGBResults:
    R: tk.IntVar
    G: tk.IntVar
    B: tk.IntVar
    _hex: tk.StringVar

    def compute_hex(self):
        r = self.__sanitize(self.R.get())
        g = self.__sanitize(self.G.get())
        b = self.__sanitize(self.B.get())
        self._hex.set(f"#{r}{g}{b}")

    def __sanitize(self, value):
        hex_val = hex(value)
        if len(hex_val) != 4:
            return f"0{hex_val[-1]}"
        return hex_val[-2:]


class HeaderFrame(ttk.Frame):
    def __init__(self, sensor, rgb_results: RGBResults, **kwds):
        super().__init__(**kwds)

        self.sensor = sensor
        self.results = rgb_results

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        ttk.Label(self, text="TCS 3200 sensor", font=("Arial", 24)).grid(column=0, columnspan=2, row=0)

        ttk.Button(self, text="Calibrate", command=self.push_calibrate_btn).grid(column=0, row=1)
        ttk.Button(self, text="Measure", command=self.push_run_btn).grid(column=1, row=1)

    def push_run_btn(self):
        out = self.sensor.read()
        self.results.R.set(out["red"])
        self.results.G.set(out["green"])
        self.results.B.set(out["blue"])
        self.results.compute_hex()

    def push_calibrate_btn(self):
        self.sensor.calibrate()


class SensorResultsPanel(ttk.LabelFrame):
    def __init__(self, rgb_results: RGBResults, **kwds):
        super().__init__(**kwds)
        self.rgb_results = rgb_results

        # Layout
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=1)
        self.columnconfigure(index=2, weight=3)
        self.columnconfigure(index=3, weight=2)

        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=1)
        self.rowconfigure(index=2, weight=1)

        # RGB labels
        ttk.Label(self, text="R:").grid(column=0, row=0)
        ttk.Label(self, text="G:").grid(column=0, row=1)
        ttk.Label(self, text="B:").grid(column=0, row=2)

        # RGB values
        ttk.Label(self, textvariable=rgb_results.R).grid(column=1, row=0)
        ttk.Label(self, textvariable=rgb_results.G).grid(column=1, row=1)
        ttk.Label(self, textvariable=rgb_results.B).grid(column=1, row=2)

        # color ractangle
        self.color_label = tk.Label(self, background=rgb_results._hex.get())
        self.color_label.grid(column=2, row=0, rowspan=3, sticky="nsew")
        rgb_results._hex.trace("w", self.update_color_label)

        # hex color label
        ttk.Label(self, textvariable=rgb_results._hex).grid(column=3, row=1)

    def update_color_label(self, *_):
        self.color_label.configure(background=self.rgb_results._hex.get())


class SensorOptionsPanel(ttk.LabelFrame):
    def __init__(self, sensor, **kwds):
        super().__init__(**kwds, text="Options")

        # vars
        self.signal_scale = tk.IntVar(value=20)
        self.measures_count = tk.IntVar()
        self.freq_cycles_count = tk.IntVar()

        self.sensor = sensor

        self.measures_count.trace("w", self.__update_measures_count)
        self.freq_cycles_count.trace("w", self.__update_freq_cycles_count)

        self.measures_count.set(3)  # to trigger update callback
        self.freq_cycles_count.set(10)  # to trigger update callback

        # Layout
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=1)
        self.columnconfigure((0, 1), weight=1)

        ttk.Label(self, text="Sensitivity:").grid(column=0, columnspan=2, row=0, sticky="w")

        ttk.Radiobutton(
            self,
            text="100%",
            value=100,
            variable=self.signal_scale,
            command=self.sensor.frequency.scale100,
        ).grid(column=0, row=1, sticky="w")

        ttk.Radiobutton(
            self,
            text="20%",
            value=20,
            variable=self.signal_scale,
            command=self.sensor.frequency.scale20,
        ).grid(column=0, row=2, sticky="w")

        ttk.Radiobutton(
            self,
            text="2%",
            value=2,
            variable=self.signal_scale,
            command=self.sensor.frequency.scale2,
        ).grid(column=0, row=3, sticky="w")

        ttk.Label(self, text="Measures mean count:").grid(column=1, row=0, sticky="wn")
        ttk.Entry(self, textvariable=self.measures_count).grid(column=1, row=1, sticky="w")

        ttk.Label(self, text="Freqency cycles count:").grid(column=1, row=2, sticky="wn")
        ttk.Entry(self, textvariable=self.freq_cycles_count).grid(column=1, row=3, sticky="w")

    def __update_measures_count(self, *_):
        val = self.measures_count.get()
        if val:
            self.sensor.frequency.set_mean_count(val)

    def __update_freq_cycles_count(self, *_):
        val = self.freq_cycles_count.get()
        if val:
            self.sensor.frequency.set_cycles_count(val)


class App(tk.Tk):
    def __init__(self, tcs_3200):
        super().__init__()
        self.title("TCS 3200")
        self.geometry("400x400")
        self.configure(padx=BASE_PADDING, pady=BASE_PADDING)

        # Create the application variable.
        self.results = RGBResults(
            R=tk.IntVar(),
            G=tk.IntVar(),
            B=tk.IntVar(),
            _hex=tk.StringVar(value="#abcdef"),
        )

        HeaderFrame(sensor=tcs_3200, rgb_results=self.results, master=self).pack(fill="both", expand=True)

        SensorResultsPanel(self.results, master=self).pack(fill="both", expand=True, pady=(0, 20))

        SensorOptionsPanel(sensor=tcs_3200, master=self, padding=BASE_PADDING).pack(
            anchor="w", fill="both", expand=True
        )

        ttk.Label(self, text="Szymon Rykała", font=("Arial", 8)).pack(
            side="bottom", anchor="se", pady=(BASE_PADDING, 0)
        )
