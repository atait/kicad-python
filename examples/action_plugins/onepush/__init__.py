import traceback
import os
import sys

ap_dir = os.path.dirname(os.path.abspath(__file__))
if ap_dir not in sys.path:
    sys.path.insert(0, ap_dir)

try:
    from onepush.action_onepush import OnePush
    OnePush().register() # Instantiate and register to Pcbnew
except Exception as e:
    try:
        from kigadgets import notify
        notify('OnePush import failed\n' + traceback.format_exc())
    except Exception:
        pass
