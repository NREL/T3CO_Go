from pathlib import Path
import sys
from streamlit.web import cli as stcli

def main():
    sys.argv = ["streamlit", "run", str(Path(__file__).parents[1]/"app"/"t3co_app.py")]
    sys.exit(stcli.main())
    
if __name__ == '__main__':
    main()