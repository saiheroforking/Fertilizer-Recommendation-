📄 Fertilizer Recommendation System
    A smart AI-based solution for predicting plant diseases from images and recommending suitable fertilizers to improve crop health.

📚 Table of Contents
About the Project
Tech Stack Used
Dataset Structure
Model Architecture
How the System Works
Installation and Setup
Deployment
Screenshots
Future Enhancements
Contributors

🌟 About the Project
The Fertilizer Recommendation System predicts plant diseases from images using a deep learning model and suggests the most appropriate fertilizer based on the detected disease.
It empowers farmers and agricultural experts to manage plant health efficiently and boost crop yield.

🛠️ Tech Stack Used
      Front-end: HTML, CSS
      Back-end: Flask (Python)
      Machine Learning: TensorFlow, Keras
      Deployment: Gunicorn, systemd service
      Database (optional): PostgreSQL or MongoDB
      Cloud/Server: Ubuntu instance / Virtual Machine
      Authentication (optional): OAuth2
      Visualization: UML diagrams, Model graphs
🗂️ Dataset Structure
The project uses a customized folder structure:
![image](https://github.com/user-attachments/assets/9e230ffd-45f3-484f-b2e6-6bd4cbd39e85)

🧠 Model Architecture
Input Layer: (128 x 128 x 3) RGB images
Convolution Layers: 3 Conv2D + ReLU activation
Pooling Layers: MaxPooling2D
GlobalAveragePooling Layer: reduces overfitting
Dense Layer: Fully connected layers
Dropout: 0.5 rate to prevent overfitting
Output Layer: softmax activation for multi-class classification
The summary of model:
![image](https://github.com/user-attachments/assets/8ca375a0-ec6c-4044-9d5e-d6225dd8ab0f)

⚙️ How the System Works
 1. User uploads a plant image via the web application.
 2. The deep learning model predicts the disease class.
 3. Based on the disease, the system fetches the recommended fertilizer.
 4. The result (disease + fertilizer suggestion) is displayed back to the user.

✅ Example:
Input Image	Predicted Disease	Recommended Fertilizer
Banana leaf	Sigatoka	Apply Potassium fertilizer
