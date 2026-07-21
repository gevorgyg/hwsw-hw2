"""Traditional front end: one long-lived Colony instance in this process."""

from Traditional.colony import Colony


def build_commands():
    return Colony.bootstrap().command_table()
