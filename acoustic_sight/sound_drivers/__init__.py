PY_GAME = 'PyGame'
SUPER_COLLIDER = 'SuperCollider'


def get_driver(name):
    if name == PY_GAME:
        import sound_drivers.pg_tools
        return pg_tools.PGSynth, pg_tools.init_audio
    elif name == SUPER_COLLIDER:
        import sound_drivers.sc_tools
        return sc_tools.SCSynth, sc_tools.init_audio