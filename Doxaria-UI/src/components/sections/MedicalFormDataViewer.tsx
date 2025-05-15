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
                if (!imageData.id_field || !imageData.matricule_cnam) {
                        alert('Please provide both ID Field and Matricule CNAM.');
                        return;
                }
                onSave(imageData);
                setIsEditing(false);
        };

    const handleCancel = () => {
        setImageData(data);
        setIsEditing(false);
    };

    return (
        <section className="container rounded-xl my-5 self-center">
                <h3 className="flex justify-center text-3xl  p-4 text-secondary">EXTRACTED TEXT</h3>
                <div className="grid grid-cols-2 py-4">
                        {[
                                {label: "Form ID", key: "id_field"},
                                {label: "Subscriber Name", key: "adherent_name"},
                                {label: "CNAM", key: "matricule_cnam"},
                                {label: "Registration Number", key: "matricule_adherent"},
                                {label: "Cin/Passport", key: "cin_ou_passport"},
                                {label: "Address", key: "adresse_adherent"},
                                {label: "Patient Name", key: "malade_name"},
                                {label: "Birth Date", key: "date_naissance"},
                        ].map(({label, key}) => (
                            <span key={key} className="justify-start p-1 text-xl text-gray-500">
    {label}:{" "}
                                    {isEditing ? (
                                        <input
                                            type="text"
                                            value={imageData[key as keyof MedicalCareExtractedData] || ""}
                                            onChange={(e) => handleChange(key as keyof MedicalCareExtractedData, e.target.value)}
                                            className="text-xl mx-1 font-bold text-primary bg-light"
                                        />
                                    ) : (
                                        <p className="text-xl font-bold mx-2 text-primary">
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
                                        className="px-4   p-2 rounded-md hover:bg-cyan/20 hover:text-dark transition-colors ease-in-out duration-200 bg-cyan/40 text-primary  "
                                    >
                                            Save
                                    </button>
                                    <button
                                        onClick={handleCancel}
                                        className="px-4   p-2 rounded-md hover:bg-cyan/20 hover:text-dark transition-colors ease-in-out duration-200 bg-cyan/40 text-primary  "
                                    >
                                            Cancel
                                    </button>
                            </>
                        ) : (
                            <>
                                <button
                                onClick={() => setIsEditing(true)}
                     className="px-4   p-2 rounded-md hover:bg-cyan/20 hover:text-dark transition-colors ease-in-out duration-200 bg-cyan/40 text-primary  "
                >
                        Edit
                </button>
                <button
                    onClick={() => handleSave()}
                    className="px-4   p-2 rounded-md hover:bg-cyan/20 hover:text-dark transition-colors ease-in-out duration-200 bg-cyan/40 text-primary   "
                >
                        Save
                </button>
                            </>
                )}
        </div>
</section>
)
        ;
}