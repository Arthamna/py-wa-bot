import logging
import os
from app import create_app
from waitress import serve

app = create_app()


if __name__ == "__main__":
    logging.info("App Online")
    port = int(os.environ.get("PORT", 8080))
    
    serve(app, host='0.0.0.0', port=port)
    # development Replit
    # if not os.environ.get('REPL_SLUG'):
    #     app.run(host='0.0.0.0', port=port)
    # else:
    # flask dev
    # app.run(host="0.0.0.0", port=8000)
    


