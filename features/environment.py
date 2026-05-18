"""
Behave environment hooks.
"""


def before_all(context):
    context.config.stdout_capture = False
    context.config.stderr_capture = False
