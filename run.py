import logging
import os
from app import create_app
from waitress import serve

app = create_app()

if __name__ == "__main__":
    logging.info("App Online")
    port = int(os.environ.get("PORT", 8080))
    
    # development Replit
    if os.environ.get('REPL_SLUG'):
        app.run(host='0.0.0.0', port=port)
    else:
        serve(app, host='0.0.0.0', port=port)
    # flask dev
    # app.run(host="0.0.0.0", port=8000)
    


