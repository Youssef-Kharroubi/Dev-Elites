import {useEffect, useState} from "react";
import axios from "axios";
import PrescriptionDataViewer from "./PrescriptionDataViewer.tsx";
import PrescriptionExtractedData from "../../models/PrescriptionExtractedData.ts";

const exampleData: PrescriptionExtractedData = {
    name: "John Doe",
    drName: "Jane Doe",
    cin: "123456789",
    invoiceNumber: "123456",
    medicines: "Paracetamol, Ibuprofen",
};



export default function PrescriptionModelForm() {
    const [selectedFile, setSelectedFile] = useState<File[] | []>([]);
    const [fileType, setFileType] = useState("");
    const [numberOfFiles, setNumberOfFiles] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [enableSubmit, setEnableSubmit] = useState<boolean>(false);
    const allowedFileTypes = ['image/png', 'image/jpeg', 'image/gif'];
    const [extractedData, setExtractedData] = useState<PrescriptionExtractedData | null>(null);
    const [saveStatus, setSaveStatus] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);



    const handleSaveData = async (data: PrescriptionExtractedData & { id_medical_care_form: string; medications: string[] }) => {
        if (!data.id_medical_care_form || !data.medications?.length) {
            setSaveStatus({
                type: 'error',
                message: 'Invalid data: ID and medications are required',
            });
            return;
        }

        try {
            const response = await fetch(import.meta.env.VITE_SAVE_PRESCRIPTION_DATA_API, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    id_medical_care_form: data.id_medical_care_form,
                    medications: data.medications,
                }),
            });

            const result = await response.json();
            if (response.ok) {
                setSaveStatus({ type: 'success', message: "Prescription data saved successfully" });
                setExtractedData({
                    name: data.name,
                    drName: data.drName,
                    medicines: data.medications.join(', '),
                });
            } else {
                setSaveStatus({ type: 'error', message: result.error || 'Failed to save data' });
            }
        } catch (error) {
            setSaveStatus({ type: 'error', message: `Error: ${error.message}` });
        }
    };

    async function extractPrescription() {
        const API_CALL = import.meta.env.VITE_EXTRACTION_PRESCRIPTION_DATA_API;
        if (!selectedFile || selectedFile.length === 0) {
            console.error('No file selected');
            setError('No file selected');
            return;
        }
        const image = selectedFile[0];
        const formData = new FormData();
        formData.append('image', image);
        try {
            setIsUploading(true);
            const response = await axios.post(API_CALL, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            const jsonString = response.data.replace(/(\w+)(?=:)/g, '"$1"');
            const matches: { predicted_text: string; best_match: string }[] = JSON.parse(jsonString);

            const medicines = matches
                .filter((item) => item.best_match)
                .map((item) => item.best_match)
                .join(", ");

            setExtractedData({
                name: extractedData?.name || exampleData.name,
                drName: extractedData?.drName || exampleData.drName,
                cin: extractedData?.cin || exampleData.cin,
                invoiceNumber: extractedData?.invoiceNumber || exampleData.invoiceNumber,
                medicines: medicines || "",
            });
        } catch (error: any) {
            console.error('Error sending image:', error);
            setError('Failed to process image');
        } finally {
            setIsUploading(false);
        }
    }

    const onFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files: FileList | null = event.target.files;
        setNumberOfFiles(files?.length || 0);

        if (!files || files.length === 0) {
            setError('Please select at least one file');
            setSelectedFile([]);
            return;
        }
        const url = URL.createObjectURL(files[0]);
        setPreviewUrl(url);
        let allowed = true;
        for (let i = 0; i < files.length; i++) {
            if (!allowedFileTypes.includes(files[i].type)) {
                console.log(`Invalid file type: ${files[i].type}`);
                allowed = false;
                break;
            }
        }
        setEnableSubmit(allowed);

        if (allowed) {
            setSelectedFile(Array.from(files));
            await onFileUpload(files);
            setError(null);
        } else {
            setSelectedFile([]);
            setError('Please select a valid file type (PNG, JPG, or GIF)');
        }
    };
    useEffect(() => {
        return () => {
            if (previewUrl) {
                URL.revokeObjectURL(previewUrl);
            }
        };
    }, [previewUrl]);
    const onFileUpload = async (files: FileList | null) => {
        const API_URL = import.meta.env.VITE_CLASSIFICATION_API_ENDPOINT;
        if (!files || files.length === 0) {
            setError('Please select a file to upload');
            return;
        }

        setIsUploading(true);
        const formData = new FormData();

        for (let i = 0; i < files.length; i++) {
            formData.append('images', files[i]);
        }

        try {
            const response = await axios.post(API_URL, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            let results = response.data.results;
            setFileType("prescription");
            for (var s of results) {
                if (s.document_type?.toLowerCase() !== 'prescription') {
                    setEnableSubmit(false);
                    setFileType(s.document_type);
                    break;
                }
            }
        } catch (error: any) {
            console.error('Error uploading file:', error);
            const errorMessage =
                error.response?.data?.error || error.message || 'Unknown error';
            setError(`Failed to upload file: ${errorMessage}`);
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <section className="container">
            <div className="flex justify-center items-center my-5">
                <h1 className="text-4xl text-primary">Here you can digitalize your Prescription docs!</h1>
            </div>
            <div className="grid grid-cols-2 gap-4">
                <div>
                    <h3 className="flex justify-center items-center text-2xl my-5 content-center text-secondary"> UPLOAD YOUR DOCS HERE</h3>
                    {error && (
                        <div className="text-red-500 text-center mb-4">{error}</div>
                    )}
                    {isUploading && (
                        <div className="text-white text-center mb-4">Uploading...</div>
                    )}

                    <div className="flex justify-between">
                        <h3 className="m-2">Number Of Selected Files: {numberOfFiles}</h3>
                        <div className="flex justify-end align-end">
                            <button
                                type="button"
                                name="submit"
                                id="submit"
                                disabled={!enableSubmit}
                                onClick={extractPrescription}
                                className={`my-2 bg-light/10  border-1 border-cyan ${
                                    enableSubmit ? 'hover:bg-primary/30 hover:border-primary' : 'opacity-50 cursor-not-allowed'
                                }`}
                            >
                                Submit!
                            </button>
                        </div>
                    </div>
                    <div className="flex items-center justify-center w-full">
                        <label
                            htmlFor="dropzone-file"
                            className="flex flex-col items-center justify-center w-full h-full border-2 border-gray-300 border-dashed rounded-lg cursor-pointer dark:bg-light/40 hover:bg-gray-100 dark:border-gray-400 dark:hover:border-gray-400 dark:hover:bg-gray-200"
                        >
                            {previewUrl ? (
                                <img
                                    src={previewUrl}
                                    alt="Uploaded preview"
                                    className="max-h-full max-w-full object-contain p-2"
                                />
                            ) : (
                                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                                    <svg
                                        className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400"
                                        aria-hidden="true"
                                        xmlns="http://www.w3.org/2000/svg"
                                        fill="none"
                                        viewBox="0 0 20 16"
                                    >
                                        <path
                                            stroke="currentColor"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                            stroke-width="2"
                                            d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                                        />
                                    </svg>
                                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                                        <span className="font-semibold">Click to upload</span> or drag and drop
                                    </p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400">
                                        PNG, JPG or GIF (MAX. 800x400px)
                                    </p>
                                </div>
                            )}
                            <input
                                id="dropzone-file"
                                type="file"
                                className="hidden"
                                accept="image/png,image/jpeg,image/gif"
                                onChange={onFileChange}
                                disabled={isUploading}
                                multiple
                            />
                        </label>
                    </div>

                    <p id="helper-text-explanation" className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                        We’ll never share your details. Read our
                        <a href="#" className="font-medium text-blue-600 hover:underline dark:text-blue-500">
                            Privacy Policy
                        </a>.
                    </p>
                </div>
                <PrescriptionDataViewer
                    key={JSON.stringify(extractedData)}
                    data={extractedData || exampleData}
                    onSave={handleSaveData}
                />

                <div>
                    {fileType && (
                        <div className="text-green-500 text-center mb-4 font-bold text-2xl">
                            <span className="text-white">Your Files Contains Documents of Type:</span> {fileType}
                        </div>
                    )}
                </div>
                {saveStatus && (
                    <div style={{ color: saveStatus.type === 'success' ? 'green' : 'red' }}>
                        {saveStatus.message}
                    </div>
                )}
            </div>
        </section>
    );
}