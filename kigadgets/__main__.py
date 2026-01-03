""" Run one time to create links

        python -m kigadgets

    if using KiCad's bundled python (aliased/symlinked to kipython), then

        kipython -m kigadgets
"""

from kigadgets.environment import cl_main

def main() -> None:
    cl_main()

if __name__ == "__main__":
    main()
