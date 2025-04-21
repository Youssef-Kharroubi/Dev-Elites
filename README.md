# Medical Handwriting Recognition and Retrieval System

## Overview
This project aims to develop a system capable of recognizing and retrieving handwritten data from medical documents. The solution is designed to enhance the efficiency and accuracy of data processing in the healthcare domain. It was developed as part of the Integrated Project course at Esprit University by Dev-Elites.

## Features
- Handwriting recognition from scanned medical documents.
- Data extraction and structured storage for easy retrieval.
- Search functionality for locating specific data within processed documents.
- User-friendly interface for uploading and managing documents.

## Tech Stack

### Frontend
- **Framework:** React.js
- **Styling:** Tailwind CSS
- **State Management:** Redux Toolkit

### Backend
- **Framework:** Flask
- **Database:** Azure cosmos DB / Blob Storage
- **OCR Integration:** TRocr 
- **Classification:** Our Own CNN model 

### Other Tools
- **Version Control:** Git and GitHub
- **Deployment:** Docker and Azure

### Root Structure
```
medical-handwriting-recognition/  
├── Backend/  
│   ├── Serving-Backend/           
│   └── Training-Pipeline/                       
├── Docker/  
│   ├── README.md                 
│   ├── requirements.txt/ 
│   ├── serving.Dockerfile/            
│   └── training.Dockerfile/                 
├── Doxaria-UI/  
│   ├── src/
│        ├── components/
│        └── pages/                          
└── README.md
```
---

## Getting Started



