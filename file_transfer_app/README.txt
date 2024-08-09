File Transfer App Guide (INITIALIZATION FOR ADMINS SKIP TO STEP 3 IF ALREADY INITIALIZED)
1. Installation
Ensure that you have Django installed. If not, you can install it using the following commands:

pip install django

Create a new Django project (if you haven't already) using:

django-admin startproject myproject
Create a new Django app within your project:

cd myproject
python manage.py startapp file_transfer_app
Copy the provided views.py, models.py, and urls.py into the file_transfer_app directory.

Update your project's urls.py to include the file transfer app's URLs. Replace the existing content with the provided urls.py.

Run the migrations:
python manage.py makemigrations
python manage.py migrate

2. Set Up Encryption Key
In the file_transfer_app directory, create an empty file named encryption_key.key. This file will store the encryption key.

3. Run the Development Server
Start the Django development server using the following command:

python manage.py runserver


You can then visit http://127.0.0.1:8000/ in your web browser to access the home page.

============================================================================================



GUIDE FOR NON-ADMIN USERS
1. User Authentication
Navigate to the signup page by clicking the "Signup" link on the home page.

Create a new account by providing a username, email, and password. Ensure that the password meets the specified requirements.

Once signed up, you can log in using the "Login" link on the home page.

2. Upload Files
After logging in, navigate to the "Upload File" page by clicking the "Upload File" link.

Upload a text file (.txt) by providing a title and selecting a file to upload. Click the "Upload" button.

The uploaded files will be listed on the "Upload File" page.

3. Share Files
To share a file, click the "Share" link next to the file you want to share.

Enter the username of the user you want to share the file with and click the "Share" button.

Shared files will be accessible to the specified user on their "Download" page.

4. Download Files
Navigate to the "Download" page by clicking the "Download" link.

Files shared with you will be listed, and you can download them by clicking the respective links.

5. Remove Files
To remove a file, click the "Remove" link next to the file you want to remove.

The file will be deleted, and you will receive a confirmation message.

6. Logout
To log out, click the "Logout" link on the home page.





Note:
The app restricts file uploads to text files (.txt) only.
The encryption key is crucial for decrypting files, so ensure the encryption_key.key file is present.
These guides cover the basic functionality of the file transfer app. You can customize and extend the app based on your requirements.
