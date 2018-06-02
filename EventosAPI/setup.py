import sys
import app.app as app

CURRENT_PYTHON = sys.version_info[:2]
REQUIRED_PYTHON = (3, 5)
if CURRENT_PYTHON < REQUIRED_PYTHON:
    sys.stderr.write("""
==========================
Unsupported Python version You need at least python 3.5
==========================
""")
    sys.exit(1)
def install_dependencies():
    import pip
    pip.main(['install', 'flask'])
    pip.main(['install', 'flask-mysql'])
    print("Done. Please before runing the PromosAPI, first follow the next steps:")
    sys.stderr.write("""
    ==========================
    1.- Copy the app/config/config.cfg.example to app/config/config.cfg
    2.- Fill the database configuration in the config.cfg file.
    ==========================
    """)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == 'install':
            install_dependencies()
        elif sys.argv[1] == 'run':
            app.start()
