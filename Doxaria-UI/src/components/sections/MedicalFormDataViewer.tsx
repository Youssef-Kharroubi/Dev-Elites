import {useState} from "react";

interface DataExtracted {
        id_form: String,
        subscriber_name:String,
        cnam_code:String,
        registration_number: String,
        cin_or_passport:String,
        address: String,
        patient_name: String,
        birth_date:String,

}
export default function  MedicalFormDataViewer(){
        const [imageData, setImageData] = useState<DataExtracted>({
                id_form:"8753473", subscriber_name:"Ben Chedli Hichem", cnam_code:"1518695109", registration_number:"686", cin_or_passport:"04635293", address: "32 RUE 8601 CHARGUIA 1 TUNIS", patient_name: "Hichem Bchurg", birth_date: "2002-02-02", 
        });


return (
    <section className="container border-2 border-white rounded-xl my-3">
            <h3 className="flex justify-center text-4xl font-bold p-4">Extracted Text</h3>
            <div className="grid grid-cols-2 py-4">
                    <span className="flex justify-center p-2 text-2xl text-gray-500 " > Form Id: <p className="text-2xl font-bold mx-2 text-white">{imageData.id_form}</p> </span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 " > Subscriber name: <p className="text-2xl font-bold mx-2 text-white">{imageData.subscriber_name}</p> </span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 "> Cnam code: <p className="text-2xl font-bold mx-2 text-white ">{imageData.cnam_code} </p></span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 "> Registration Number: <p className="text-2xl font-bold mx-2  text-white">{imageData.registration_number}</p></span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 "> Cin or passport: <p className="text-2xl font-bold mx-2  text-white">{imageData.cin_or_passport}</p></span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 "> Address: <p className="text-2xl font-bold mx-2  text-white">{imageData.address}</p></span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 "> Patient Name: <p className="text-2xl font-bold mx-2  text-white">{imageData.patient_name}</p></span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 "> Birth date: <p className="text-2xl font-bold mx-2  text-white">{imageData.birth_date}</p></span>

            </div>
    </section>
);
}