import {useEffect, useState} from "react";
import MedicalCareExtractedData from "../../models/MedicalCareExtractedData.ts";

interface MedicalFormDataViewerProps {
    data: MedicalCareExtractedData;
    onSave: (data: MedicalCareExtractedData) => void;
}

export default function MedicalFormDataViewer({ data, onSave }: MedicalFormDataViewerProps) {
    const [imageData, setImageData] = useState<MedicalCareExtractedData>(data);
    const [isEditing, setIsEditing] = useState(false);
    console.log(data);
    useEffect(() => {
        console.log(data.id_field);

    }, []);
    const handleChange = (field: keyof MedicalCareExtractedData, value: string) => {
        setImageData((prev) => ({ ...prev, [field]: value }));
    };

    const handleSave = () => {
        onSave(imageData);
        setIsEditing(false);
    };

    const handleCancel = () => {
        setImageData(data);
        setIsEditing(false);
    };

    return (
        <section className="container rounded-xl my-5 self-center">
            <h3 className="flex justify-center text-3xl p-4">Extracted Text</h3>
            <div className="grid grid-cols-2 py-4">
                {[
                    { label: "Form ID", key: "id_field" },
                    { label: "Subscriber Name", key: "adherent_name" },
                    { label: "CNAM", key: "matricule_cnam" },
                    { label: "Registration Number", key: "matricule_adherent" },
                    { label: "Cin/Passport", key: "cin_ou_passport" },
                    { label: "Address", key: "adresse_adherent" },
                    { label: "Patient Name", key: "malade_name" },
                    { label: "Birth Date", key: "date_naissance" },
                ].map(({ label, key }) => (
                    <span key={key} className="justify-start p-1 text-xl text-gray-500">
    {label}:{" "}
                        {isEditing ? (
                            <input
                                type="text"
                                value={imageData[key as keyof MedicalCareExtractedData] || ""}
                                onChange={(e) => handleChange(key as keyof MedicalCareExtractedData, e.target.value)}
                                className="text-xl mx-1 text-white bg-dark"
                            />
                        ) : (
                            <p className="text-xl mx-2 text-white">
                                {imageData[key as keyof MedicalCareExtractedData] || imageData[key as keyof MedicalCareExtractedData] === ""
                                    ? imageData[key as keyof MedicalCareExtractedData]
                                    : "N/A"}
                            </p>
                        )}
</span>

                ))}
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
                        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
                    >
                        Edit
                    </button>
                )}
            </div>
        </section>
    );
}