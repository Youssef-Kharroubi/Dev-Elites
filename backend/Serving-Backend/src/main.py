from .api.app import app
from dotenv import load_dotenv

import os
from azureml.core import Workspace
from .services.model_loader import download_model
from .api.app import create_app

if __name__ == "__main__":
    load_dotenv()
    app.run()

    try:
        ws = Workspace.from_config()
        model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "models", "CNN_model.h5"))

        if os.path.exists(model_path):
            print(f"Model already exists at: {model_path}")
        else:

            model_path = download_model(ws)
            print(f"Model downloaded and ready at: {model_path}")

        app = create_app(model_path)

        app.run(debug=True, host="0.0.0.0", port=5000)
    except Exception as e:
        print(f"Failed to start app: {str(e)}")
        raise