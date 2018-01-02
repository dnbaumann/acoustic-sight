PY_AUDIO = 'PyAudio'
PY_GAME = 'PyGame'
SUPER_COLLIDER = 'SuperCollider'


def get_driver(name):
    if name == PY_AUDIO:
        import sonification.sound_drivers.pa_tools as pa_tools
        return pa_tools.PASynth, pa_tools.init_audio
    elif name == PY_GAME:
        import sonification.sound_drivers.pg_tools as pg_tools
        return pg_tools.PGSynth, pg_tools.init_audio
    elif name == SUPER_COLLIDER:
        import sonification.sound_drivers.sc_tools as sc_tools
        return sc_tools.SCSynth, sc_tools.init_audio
