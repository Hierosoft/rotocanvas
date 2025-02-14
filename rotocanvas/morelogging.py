# region same as hierosoft

def formatted_ex(ex):
    """Similar to traceback.format_exc but works on any not just current
    (traceback.format_exc only uses exception occurring, not argument!)
    """
    return "{}: {}".format(type(ex).__name__, ex)

# endregion same as hierosoft