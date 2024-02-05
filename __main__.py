from app import App
from TCS_3200 import TCS3200

# output frequency scaling
S0 = 17
S1 = 27

# photodiode select
S2 = 23
S3 = 24

LED_POWER = 22
SIGNAL = 25

sensor = TCS3200(
    fscale0=S0,
    fscale1=S1,
    pdiode0=S2,
    pdiode1=S3,
    led=LED_POWER,
    signal=SIGNAL,
)

app = App(tcs_3200=sensor)


def shutdown_handler():
    sensor.cleanup()
    app.destroy()


app.protocol("WM_DELETE_WINDOW", shutdown_handler)

try:
    app.mainloop()
except Exception:
    sensor.cleanup()
    app.destroy()
