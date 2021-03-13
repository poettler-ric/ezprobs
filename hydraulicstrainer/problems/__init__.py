#!/usr/bin/env python3


class Parameter:
    def __init__(
        self,
        name,
        display,
        val_min,
        val_max,
        val_step=1,
        val_initial=0,
        unit="",
        description="",
    ):
        if val_initial < val_min or val_initial > val_max:
            raise ValueError(
                f"initial value ({val_initial}) must be between minimum ({val_min}) and maximum ({val_max})"
            )

        if val_initial % val_step != 0:
            raise ValueError(
                f"initial value ({val_initial}) must be divisible by step ({val_step})"
            )

        self.name = name
        self.unit = unit
        self.display = display
        self.description = description
        self.val_initial = val_initial
        self.val_min = val_min
        self.val_max = val_max
        self.val_step = val_step


class Plot:
    """Plot which should appear over the parameter section."""

    def __init__(self, url, alt="", caption=""):
        self.url = url
        self.alt = alt
        self.caption = caption
