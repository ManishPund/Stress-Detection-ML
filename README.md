# Stress Detection Using Machine Learning

## Overview
This project leverages machine learning techniques to detect stress from facial expressions. It provides real-time analysis and tracks stress levels over time, making it easier for users to manage their emotional well-being. The system is equipped with functionalities for image uploads, live feed detection, and user account management.

## Features
- **User Registration and Login:** Secure user accounts with admin approval.
- **Stress Detection:** Analyze facial expressions from uploaded images or live video feeds to classify emotions.
- **Result Tracking:** Group results by date and display them in an organized table for trend analysis.
- **Admin Management:** Admins can approve or deactivate user accounts.
- **Real-Time Feedback:** Option to capture and analyze images from live video streams.
- **Data Security:** Ensure the privacy of user data with secure storage.

## Tech Stack
- **Backend:** Python, Django
- **Frontend:** HTML, CSS, Bootstrap
- **Database:** SQLite
- **Libraries:** OpenCV, Scikit-learn

## Installation

### Prerequisites
- Python 3.8+
- Virtual environment (optional but recommended)

### Steps
1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/Stress-Detection-ML.git
   cd Stress-Detection-ML
2. **Set up a virtual environment (optional):**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate

   ```bash
   pip install -r requirements.txt
   
   
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   Start the development server:
   
   ```bash
   python manage.py runserver
   Access the application: Open your browser and navigate to http://127.0.0.1:8000.

## Usage
User: Register, upload images, or use live feed for stress detection. View stress levels in the results table.
Admin: Manage user accounts and monitor activity.
Future Enhancements
Incorporate multimodal stress indicators such as voice or text analysis.
Improve the machine learning model for higher accuracy.
Develop a mobile application for better accessibility.
Integrate cloud storage for scalability.


## Contact
For any inquiries, feel free to reach out at manishpund@outlook.com.
