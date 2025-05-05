import MedicalFormDataViewer from "./MedicalFormDataViewer.tsx";
import { useState } from 'react';
import axios from "axios";

export default function MedicalModelForm (){
    const [selectedFile, setSelectedFile] = useState<FileList | null>(null);
    const [insuranceCompany, setInsuranceCompany] = useState<string[]>([]);
    const [fileType, setFileType] = useState<string>('');
    const [numberOfFiles, setNumberOfFiles] = useState<number>(0);
    const [error, setError] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState<boolean>(false);
    const [enableSubmit, setEnableSubmit] = useState<boolean>(false);
    const allowedFileTypes = ['image/png', 'image/jpeg', 'image/gif'];

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
            setError('Please select a valid file type (PNG, JPG, or GIF)');
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
            const results = response.data.results;
            const documentTypes = results.map((result: any) => result.document_type?.toLowerCase());
            const insuranceCompanies = results.map((result: any) => result.insurance_company || 'Unknown');

            const firstNonMedicalType = documentTypes.find((type: string) => type !== 'medical care form') || 'medical care form';
            setFileType(firstNonMedicalType);
            setInsuranceCompany(insuranceCompanies);

            const allMedicalCareForms = documentTypes.every((type: string) => type === 'medical care form');
            setEnableSubmit(allMedicalCareForms);
        } catch (error: any) {
            console.error('Error uploading file:', error);
            const errorMessage = error.response?.data?.error || error.message || 'Unknown error';
            setError(`Failed to upload file: ${errorMessage}`);
        } finally {
            setIsUploading(false);
        }
    };
    return (
        <section className="container">
            <div className="flex justify-center items-center my-5">
                <h1 className="text-4xl text-light ">Here you can digitalize your Medical Care Form  docs!</h1>
            </div>
            <div>
                <h3 className=" flex justify-center items-center text-2xl my-5">Just upload your docs here!</h3>
                {error && (
                    <div className="text-red-500 text-center mb-4">{error}</div>
                )}
                {isUploading && (
                    <div className="text-white text-center mb-4">Uploading...</div>
                )}
                <h3 className="m-2">Number Of Selected Files : {numberOfFiles} </h3>
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
                        <input id="dropzone-file" type="file" onChange={onFileChange}
                               className="hidden" accept="image/png,image/jpeg,image/gif"
                               disabled={isUploading} multiple/>
                    </label>
                </div>

                <p id="helper-text-explanation" className="mt-2 text-sm text-gray-500 dark:text-gray-400">We’ll
                    never share your details. Read our
                    <a href="#" className="font-medium text-blue-600 hover:underline dark:text-blue-500">
                        Privacy Policy
                    </a>.
                </p>
                <div className="flex justify-end align-end">
                    <button type="button" name="submit" id="submit"
                            disabled={!enableSubmit}
                            className={`my-2 bg-light/10 border-0 ${
                                enableSubmit ? 'hover:bg-light/30' : 'opacity-50 cursor-not-allowed'
                            }`}>Submit !
                    </button>

                </div>
            </div>
            <div>
                {fileType && insuranceCompany.length > 0 && (
                    <div className="text-green-500 text-center mb-4 font-bold text-2xl">
                        <span className="text-white">Your Files Contains : </span> {fileType} <br />
                        <span className="text-white">Insurance companies: </span> {insuranceCompany.join(', ')}
                    </div>
                )}
            </div>
            <MedicalFormDataViewer/>

        </section>
    );
}
