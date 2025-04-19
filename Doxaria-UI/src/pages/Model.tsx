import PrescriptionModelForm from "../components/sections/PrescriptionModelForm.tsx";
import MedicalModelForm from "../components/sections/MedicalModelForm.tsx";
import {useState} from "react";

export default function Model(){

    const [active,setActive] = useState<Number>(0);
    function handlePrescription(){
        setActive(0)
    }
    function handleMedicalForm(){
        setActive(1)
    }

    const RenderForm = (active:Number) =>{
        if(active==0){
            return(
                <PrescriptionModelForm/>
            )
        }else{
            return(
                <MedicalModelForm/>
            )
        }
    }
    return(
        <section className="container">
            <div className="flex my-4 gap-x-4  ">
                <button onClick={handlePrescription} className="hover:bg-light/30 border-0" >Prescription</button>
                <button onClick={handleMedicalForm} className="hover:bg-light/30 border-0" >Medical Care Form</button>
            </div>
            <div>
                {
                    RenderForm(active)
                }
            </div>

        </section>


    );
}