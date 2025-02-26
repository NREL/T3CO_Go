from pathlib import Path
import sys
from streamlit.web import cli as stcli
from t3co.utilities import demo_inputs_installer

def main():
    if not (Path(__file__).parents[3]/"demo_inputs").exists():
        demo_inputs_installer.copy_demo_input_files(Path(__file__).parents[3])
    sys.argv = ["streamlit", "run", str(Path(__file__).parents[1]/"app"/"t3co_app.py")]
    print(sys.argv)
    sys.exit(stcli.main())
    
if __name__ == '__main__':
    main()