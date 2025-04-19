export default function AboutUs(){
    return(
        <section className="container p-4">
            <h1 className="flex justify-center m-4">ABOUT US</h1>
            <div className="flex justify-center">
                <img src="../../../public/images/aboutUs.webp" alt="About Us" width="450"
                     className=" m-4"/>
            </div>
            <div className="flex justify-center mt-5 ">
                <span className="text-xl text-center">At <span className="font-bold ">Doxaria</span>, we're transforming the way medical data is accessed and utilized.
                    Our mission is to simplify and accelerate the extraction of critical information from medical documents using cutting-edge image processing and machine learning technologies.
                    From handwritten prescriptions to lab results, our system is designed to turn unstructured medical imagery into organized, searchable,
                    and meaningful data—ready to be used by healthcare professionals and researchers.</span>
            </div>
            <div className="grid grid-cols-2 mt-5  gap-3">
                <p className="text-md text-center ">What makes us different? We’re not just a team—we’re a vision-driven collective of
                    passionate university students from <span className="font-bold ">ESPRIT </span>, specializing in
                    Data Science. With a strong foundation in
                    machine learning, and computer vision, we are
                    solving a real problem in the healthcare industry:
                    <span className="font-bold ml-1">Accessibility to clean, structured Data.</span></p>
                <p className="text-md text-center">
                    As emerging Data Scientists and Engineers, we believe in building Intelligent, Ethical, and reliable
                    solutions that make a difference.
                    Our diverse backgrounds and collaborative spirit fuel a startup culture that’s both <span
                    className="font-bold ml-1"> research-intensive</span> and <span
                    className="font-bold ml-1"> action-driven.</span>
                    We're still at the beginning of our journey, but our goal is clear

                </p>
                <p className="col-span-2 flex justify-center font-bold text-2xl my-4">Let’s Shape The Future Of Medical
                    Data—Together.</p>
            </div>

        </section>
    );
}