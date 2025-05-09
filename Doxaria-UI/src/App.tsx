import Header from "./components/layout/Header.tsx";

import {BrowserRouter as Router,Routes,Route} from "react-router-dom";
import Home from "./pages/Home.tsx";
import Model from "./pages/Model.tsx";
import AboutUs from "./components/sections/AboutUs.tsx";
import MedicalModelForm from "./components/sections/MedicalModelForm.tsx";
import PrescriptionModelForm from "./components/sections/PrescriptionModelForm.tsx";

function App() {


  return (
      <Router>
          <div className="min-h-screen bg-dark text-light">
              <Header/>
              <Routes>
                  <Route path="/" element={<Home />}/>
                  <Route path="/Model" element={<Model/>}/>
                  <Route path="/AboutUs" element={<AboutUs/>}/>
                  <Route path="/Medical-Form" element={<MedicalModelForm/>}/>
                  <Route path="/Prescription" element={<PrescriptionModelForm/>}/>
              </Routes>
          </div>
      </Router>
)
}

export default App
