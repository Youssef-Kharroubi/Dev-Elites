import {useState} from "react";
import PrescriptionExtractedData from "../../models/PrescriptionExtractedData.ts"



interface PrescriptionDataViewerProps {
    initialData: PrescriptionExtractedData;
    onSave: (data: PrescriptionExtractedData) => void;
}

export default function PrescriptionDataViewer({ initialData, onSave }: PrescriptionDataViewerProps){
    const [imageData, setImageData] = useState<PrescriptionExtractedData>(initialData);
    const [isEditing, setIsEditing] = useState(false);

    const handleChange = (field: keyof PrescriptionExtractedData, value: string) => {
        setImageData((prev) => ({ ...prev, [field]: value }));
    };

    const handleSave = () => {
        onSave(imageData);
        setIsEditing(false);
    };

    const handleCancel = () => {
        setImageData(initialData);
        setIsEditing(false);
    };

    return (
        <section className="container rounded-xl my-5 self-center">
            <h3 className="flex justify-center text-3xl  p-4">Extracted Text</h3>
            <div className="grid grid-cols-2 py-4">
        <span className=" justify-start p-1 text-xl text-gray-500">
          Patient Name:{" "}
            {isEditing ? (
                <input
                    type="text"
                    value={imageData.name}
                    onChange={(e) => handleChange("name", e.target.value)}
                    className="text-xl mx-1 text-white bg-dark "
                />
            ) : (
                <p className="text-xl font-bold mx-2 text-white">{imageData.name}</p>
            )}
        </span>
                <span className=" justify-center p-1 text-xl text-gray-500 ">
          Doctor Name:{" "}
                    {isEditing ? (
                        <input
                            type="text"
                            value={imageData.drName}
                            onChange={(e) => handleChange("drName", e.target.value)}
                            className="text-xl mx-1 text-white bg-dark rounded "
                        />
                    ) : (
                        <p className="text-xl font-bold mx-2 text-white">{imageData.drName}</p>
                    )}
        </span>
                <span className=" justify-center p-1 text-xl text-gray-500 ">
          Medicines:{" "}
                    {isEditing ? (
                        <input
                            type="text"
                            value={imageData.medicines || ""}
                            onChange={(e) => handleChange("medicines", e.target.value)}
                            className="text-xl mx-1 text-white bg-dark rounded p-1"
                        />
                    ) : (
                        <p className="text-xl font-bold mx-2 text-white">{imageData.medicines || "N/A"}</p>
                    )}
        </span>
            </div>
            <div className="flex justify-end gap-4 p-4">
                {isEditing ? (
                    <>
                        <button
                            onClick={handleSave}
                            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
                        >
                            Save
                        </button>
                        <button
                            onClick={handleCancel}
                            className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
                        >
                            Cancel
                        </button>
                    </>
                ) : (
                    <button
                        onClick={() => setIsEditing(true)}
                        className="px-4 text-content  p-2 rounded-md hover:bg-light/20 hover:text-light transition-colors ease-in-out duration-200  "
                    >
                        Edit
                    </button>
                )}
            </div>
        </section>
    );
}