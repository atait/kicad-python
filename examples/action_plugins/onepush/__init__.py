import traceback

try:
    from onepush.action_onepush import OnePush
    OnePush().register() # Instantiate and register to Pcbnew
except Exception as e:
    try:
        from kigadgets import notify
        notify('OnePush import failed\n' + traceback.format_exc())
    except Exception:
        pass
