

export default function Model(){

    return(
        <section className="container">


            <div className="my-4 gap-x-4  py-40">
                <h2 className="flex justify-center items-center text-2xl font-bold my-4">CHOOSE DOC TYPE ! </h2>
                <div className="flex justify-center items-center ">
                    <a href="/Prescription"
                       className="hover:bg-light/30 border-2 border-gray-600 p-14 rounded-md m-4 text-2xl font-bold ">Prescription</a>
                    <a href="/Medical-Form"
                       className="hover:bg-light/30 border-2 border-gray-600 p-14 rounded-md m-4 text-2xl font-bold">Medical
                        Care </a>
                </div>
            </div>

        </section>


    );
}