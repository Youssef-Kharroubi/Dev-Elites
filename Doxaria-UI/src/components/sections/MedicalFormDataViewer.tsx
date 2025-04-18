import {useState} from "react";

interface DataExtracted {
        name:String,
        drName:String,
        cin:String,
        invoiceNumber:String,

}
export default function  MedicalFormDataViewer(){
        const [imageData, setImageData] = useState<DataExtracted>({
                name:"John Doe",drName:"Jane Doe",cin:"123456789",invoiceNumber:"123456"
        });


return (
    <section className="container border-2 border-white rounded-xl my-3">
            <h3 className="flex justify-center text-4xl font-bold p-4">Extracted Text</h3>
            <div className="grid grid-cols-2 py-4">
                    <span className="flex justify-center p-2 text-2xl text-gray-500 " > Name: <p className="text-2xl font-bold mx-2 text-white">{imageData.name}</p> </span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 "> Doctor Name: <p className="text-2xl font-bold mx-2 text-white ">{imageData.drName} </p></span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 "> ID Number: <p className="text-2xl font-bold mx-2  text-white">{imageData.cin}</p></span>
                    <span className="flex justify-center p-2 text-2xl text-gray-500 ">  Invoice Number: <p className="text-2xl font-bold mx-2  text-white">{imageData.invoiceNumber}</p></span>

            </div>
    </section>
);
}