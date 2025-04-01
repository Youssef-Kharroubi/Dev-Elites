import Header from "./components/layout/Header.tsx";

import {BrowserRouter as Router,Routes,Route} from "react-router-dom";
import Home from "./pages/Home.tsx";
import Model from "./pages/Model.tsx";

function App() {


  return (
      <Router>
          <div className="min-h-screen bg-dark text-light">
              <Header/>
              <Routes>
                  <Route path="/" element={<Home />}/>
                  <Route path="/Model" element={<Model/>}/>
              </Routes>
          </div>
      </Router>
)
}

export default App
