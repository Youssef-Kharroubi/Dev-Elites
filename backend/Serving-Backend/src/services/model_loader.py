from azureml.core import Model
import os

def download_model(workspace):
    """
    Download the CNN_model from Azure ML Model Registry.

    Args:
        workspace: Azure ML Workspace object

    Returns:
        str: Path to the downloaded .h5 file
    """
    model_name = "CNN_model"
    target_path = os.path.join(os.path.dirname(__file__), "..", "models")

    os.makedirs(target_path, exist_ok=True)

    target_path = os.path.abspath(target_path)
    print(f"Downloading model to: {target_path}")

    try:
        model = Model(workspace=workspace, name=model_name, version=1)
        model_path = model.download(target_dir=target_path, exist_ok=True)
        print(f"Model downloaded to: {model_path}")

        for root, _, files in os.walk(model_path):
            for file in files:
                if file == "CNN_model.h5":
                    return os.path.join(root, file)

        raise FileNotFoundError("CNN_model.h5 not found in downloaded files")
    except Exception as e:
        raise RuntimeError(f"Failed to download model: {str(e)}") from e