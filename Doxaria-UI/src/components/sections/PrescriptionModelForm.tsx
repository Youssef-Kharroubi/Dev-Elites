import {useState} from "react";
import axios from "axios";
import PrescriptionDataViewer from "./PrescriptionDataViewer.tsx";
import PrescriptionExtractedData from "../../models/PrescriptionExtractedData.ts"
const exampleData: PrescriptionExtractedData = {
    name: "John Doe",
    drName: "Jane Doe",
    cin: "123456789",
    invoiceNumber: "123456",
    medicines: "Paracetamol, Ibuprofen",
};

const handleSaveData = (data: PrescriptionExtractedData) => {
    console.log("Saved data:", data);
    // Implement actual save logic here (e.g., API call)
}

export default function PrescriptionModelForm (){
    const [selectedFile, setSelectedFile] = useState<[File] | []>();
    const [fileType, setFileType] = useState("");
    const [numberOfFiles, setNumberOfFiles] = useState(0);
    const [error, setError] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [enableSubmit, setEnableSubmit] = useState(true);
    const allowedFileTypes = [ 'image/png', 'image/jpeg', 'image/gif'];
    const [extractedData, SetExtractedData] = useState<PrescriptionExtractedData | null>(null);

    async function extractPrescription(){
        const API_CALL = import.meta.env.VITE_EXTRACTION_PRESCRIPTION_DATA_API;
        if (!selectedFile || selectedFile.length === 0) {
            console.error('No file selected');
            return;
        }
        const image = selectedFile[0];
        const formData = new FormData();
        formData.append('image', image);
        try{
            const response = await axios.post(API_CALL, formData,{
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            console.log('Backend response:', response.data);
            SetExtractedData(response.data);
        }catch(error){
            console.error('Error sending image:', error);
            throw error;
        }
    }


    const onFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const files: FileList | null = event.target.files;
        setNumberOfFiles(files?.length || 0);

        if (!files || files.length === 0) {
            setError('Please select at least one file');
            setSelectedFile(null);
            return;
        }

        let allowed = true;
        for (let i = 0; i < files.length; i++) {
            if (!allowedFileTypes.includes(files[i].type)) {
                console.log(`Invalid file type: ${files[i].type}`);
                allowed = false;
                break;
            }
        }

        if (allowed) {
            setSelectedFile(files);
            await onFileUpload(files);
            setError(null);
        } else {
            setSelectedFile(null);
            setError('Please select a valid file type (SVG, PNG, JPG, or GIF)');
        }
    };
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

            console.log('Response:', response.data);
            let results = response.data.results;
            setFileType("prescription");
            for(var s of results){
                if(s.document_type?.toLowerCase() !== 'prescription'){
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
        <section className="container" >
            <div className="flex justify-center items-center my-5">
                <h1 className="text-4xl text-light ">Here you can digitalize your Prescription docs!</h1>
            </div>
            <div className="grid grid-cols-2 gap-4">
                <div>
                <h3 className=" flex justify-center items-center text-2xl my-5">Just upload your docs here!</h3>
                {error && (
                    <div className="text-red-500 text-center mb-4">{error}</div>
                )}
                {isUploading && (
                    <div className="text-white text-center mb-4">Uploading...</div>
                )}


                    <div className="flex justify-between">
                        <h3 className="m-2">Number Of Selected Files : {numberOfFiles} </h3>
                        <div className="flex justify-end align-end">
                            <button type="button" name="submit" id="submit"
                                    disabled={!enableSubmit}
                                    onClick={extractPrescription}
                                    className={`my-2 bg-light/10 border-0 ${
                                        enableSubmit ? 'hover:bg-light/30' : 'opacity-50 cursor-not-allowed'
                                    }`}>Submit !
                            </button>

                        </div>
                    </div>
                    <div className="flex items-center justify-center w-full">
                        <label htmlFor="dropzone-file"
                               className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600">
                        <div className="flex flex-col items-center justify-center pt-5 pb-6">
                            <svg className="w-8 h-8 mb-4 text-gray-500 dark:text-gray-400" aria-hidden="true"
                                 xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 20 16">
                                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round"
                                      stroke-width="2"
                                      d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"/>
                            </svg>
                            <p className="mb-2 text-sm text-gray-500 dark:text-gray-400"><span
                                className="font-semibold">Click to upload</span> or drag and drop</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">SVG, PNG, JPG or GIF (MAX.
                                800x400px)</p>
                        </div>
                        <input id="dropzone-file" type="file" className="hidden" accept="image/png,image/jpeg,image/gif" onChange={onFileChange}
                               disabled={isUploading} multiple/>
                    </label>
                </div>

                <p id="helper-text-explanation" className="mt-2 text-sm text-gray-500 dark:text-gray-400">We’ll
                    never share your details. Read our
                    <a href="#" className="font-medium text-blue-600 hover:underline dark:text-blue-500">Privacy
                        Policy</a>.</p>


                </div>
                <PrescriptionDataViewer key={JSON.stringify(extractedData)} data={extractedData || exampleData} onSave={handleSaveData} />

                <div>
                    {fileType && (
                        <div className="text-green-500 text-center mb-4 font-bold text-2xl"><span
                            className="text-white ">Your Files Contains Documents of Type  :</span> {fileType}
                        </div>
                    )}
                </div>

            </div>

        </section>
    );
}








