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
        self.name = name
        self.unit = unit
        self.display = display
        self.description = description
        self.val_initial = val_initial
        self.val_min = val_min
        self.val_max = val_max
        self.val_step = val_step
