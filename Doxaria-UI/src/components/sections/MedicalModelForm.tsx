export default function MedicalModelForm (){
    return (
        <section className="container mx-auto">
            <div className="flex justify-center items-center my-5">
                <h1 className="text-4xl text-light ">Here you can digitalize your Medical Care Form  docs!</h1>
            </div>
            <div className="">
                <h3 className=" flex justify-center items-center text-2xl my-5">Just upload your docs here!</h3>
                <form className="">

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
                            <input id="dropzone-file" type="file" className="hidden"/>
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
                                className=" my-2 bg-light/10 hover:bg-light/30 border-0">Submit !
                        </button>
                    </div>
                </form>
            </div>

        </section>
    );
}
