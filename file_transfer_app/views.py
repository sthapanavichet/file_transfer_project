from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import FileTransfer
from .forms import FileTransferForm
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
import os
import hashlib


# Decorator to redirect if user is not logged in for certain views.
def my_login_required():
    """
    Decorator to redirect if user is not logged in for certain views.

    Returns:
        function: The decorated function.
    """

    def decorator(view_func):  # This is the actual decorator that takes a function `view_func` as an argument.
        def wrapper(request, *args,
                    **kwargs):  # This is a wrapper function that adds after calling the original `view_func`.
            if not request.user.is_authenticated:
                messages.error(request, "You must be logged in to access the URL.")
                return redirect('home')
            else:
                return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def home(request):
    """
    Renders the home page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    return render(request, 'file_transfer_app/home.html')


def user_login(request):
    """
    Handles user login.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    if request.user.is_authenticated:
        messages.error(request, "Already logged in.")
        return redirect('home')

    if request.method == 'POST':  # Check if the form is submitted using POST method.
        # Get the username and password from the form data.
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,
                            password=password)  # Authenticate the user using the provided username and password.
        if user is None:
            messages.error(request,
                           "Username or Password is incorrect.")  # If authentication fails, display an error message.
        else:
            login(request, user)
            messages.success(request,
                             "You have successfully logged in.")  # If authentication is successful, log in the user and redirect to the home page.
            return redirect('home')

    return render(request,
                  'file_transfer_app/login.html')  # If the request method is not POST, or if authentication fails, render the login page


def user_logout(request):
    """
    Handles user logout.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    if request.user.is_authenticated:  # Check if the user is authenticated before attempting to log them out.
        logout(request)
        messages.success(request, "You have successfully logged out.")

    else:
        messages.error(request,
                       "You have to be logged in to logout.")  # If not authenticated, display an error message.

    return redirect('home')  # Redirect the user to the home page, regardless of whether they were logged out or not.


def signup(request):
    """
    Handles user signup.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    # Check if the user is already authenticated, if so, redirect to the home page.
    if request.user.is_authenticated:
        messages.error(request, "Already logged in.")
        return redirect('home')

    # Check if the form is submitted using POST method.
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        invalid = False

        # Validate the user input.
        if password != confirm_password:
            messages.error(request, "Confirmation password doesn't match the original password.")
            invalid = True

        if len(password) <= 8:
            messages.error(request, "Password must be at least 8 characters.")
            invalid = True

        if not any(char.isalpha() or char.isdigit() for char in password):
            messages.error(request, "Password must contain at least one letter or number.")
            invalid = True

        if not username.isalnum():
            # cleaning the inputs to ensure that the user cant use any sql attacks to show data
            messages.error(request, "Username must only contain letters and numbers.")
            invalid = True

        if User.objects.filter(username=username):
            messages.error(request, "Username already exist.")
            invalid = True

        if invalid:
            return render(request, 'file_transfer_app/signup.html')

        # Create a new user with the provided information.
        user = User.objects.create_user(username, email, password)
        user.save()
        # Display a success message and redirect to the home page.
        messages.success(request, "Your account has been successfully created")
        return redirect('home')
    return render(request, 'file_transfer_app/signup.html')


def calculate_file_hash(file_path, hash_algorithm='sha256'):
    """Calculate the hash of a file."""
    hash_object = hashlib.new(hash_algorithm)

    with open(file_path, 'rb') as file:
        # Read the file in chunks to avoid loading the entire file into memory
        while chunk := file.read(8192):
            hash_object.update(chunk)

    return hash_object.hexdigest()


def save_hash_to_file(hash_value, original_hash_path):
    """Save the hash value to a text file."""
    print("am here")
    with open(original_hash_path, 'w') as hash_file:
        hash_file.write(hash_value)


@my_login_required()
def upload_file(request):
    """
    Handles file upload.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """
    # Check if the form is submitted using POST method.
    if request.method == 'POST':
        form = FileTransferForm(request.POST, request.FILES)
        if form.is_valid():
            if not form.instance.file.name.endswith('.txt'):
                messages.error(request, "Only text files (.txt) are allowed.")
                return redirect('upload_file')

            form.instance.uploader = request.user
            form.save()
            form.instance.shared_with.add(request.user)
            form.save()

            file_path = form.instance.file.path
            folder_path = os.path.dirname(file_path)
            file_name, file_extension = os.path.splitext(os.path.basename(file_path))
            hashed_file_name = f"{file_name}_hash{file_extension}"
            original_hash_path = os.path.join(folder_path, hashed_file_name)

            key = get_key(request)  # Get the encryption key.
            cipher_suite = Fernet(key)  # Create a Fernet cipher suite with the encryption key.

            # Encrypt the content of the uploaded file.
            with open(form.instance.file.path, 'rb') as original_file:
                original_content = original_file.read()
                encrypted_content = cipher_suite.encrypt(original_content)

            # Write the encrypted content back to the file.
            with open(form.instance.file.path, 'wb') as encrypted_file:
                encrypted_file.write(encrypted_content)

            messages.success(request, f"'{form.instance.title}' has been successfully uploaded.")
            original_hash = calculate_file_hash(file_path)
            save_hash_to_file(original_hash, original_hash_path)
            print(original_hash)
            return redirect('upload_file')
    else:
        form = FileTransferForm()

    # Display the files uploaded by the current user
    files = FileTransfer.objects.filter(uploader=request.user)

    return render(request, 'file_transfer_app/upload_file.html', {'form': form, 'files': files})


@my_login_required()
def download_page(request):
    """
    Renders the download page.

    Args:
        request (HttpRequest): The request object.

    Returns:
        HttpResponse: The response object.
    """

    # Retrieve files that are shared with the current user.
    files = FileTransfer.objects.filter(shared_with=request.user)
    # Render the download_page.html template with the list of shared files.
    return render(request, 'file_transfer_app/download_page.html', {'files': files})


def load_hash_from_file(hash_file_path):
    """Load the file path and hash value from a text file."""
    with open(hash_file_path, 'r') as hash_file:
        file_content = hash_file.read()
    lines = file_content.splitlines()

    old_file_hash = lines[0]
    return old_file_hash


def check_file_integrity(request, saved_hash_path, file_path, hash_algorithm='sha256'):
    """Check if a file has been tampered with."""
    original_hash = load_hash_from_file(saved_hash_path)
    current_hash = calculate_file_hash(file_path, hash_algorithm)
    print(original_hash)
    print(current_hash)

    if current_hash != original_hash:
        messages.error(request, "File has been tempered with.")
        return True



@my_login_required()
def download_file(request, file_id):
    """
    Handles file download.

    Args:
        request (HttpRequest): The request object.
        file_id (int): The ID of the file to be downloaded.

    Returns:
        HttpResponse: The response object.
    """

    try:
        file = get_object_or_404(FileTransfer, id=file_id)
    except:
        messages.error(request, "File doesn't exist.")
        return redirect('home')

    if request.user not in file.shared_with.all():
        messages.error(request, "You do not have access to the file.")
        return redirect('home')

    # Decrypt the content before sending it as a response
    path = os.path.dirname(__file__)
    key = get_key(request)
    cipher_suite = Fernet(key)

    folder_path = os.path.dirname(file.file.path)
    file_name, file_extension = os.path.splitext(os.path.basename(file.file.path))
    hashed_file_name = f"{file_name}_hash{file_extension}"
    saved_hash_path = os.path.join(folder_path, hashed_file_name)
    encrypted_content = b''
    with open(file.file.path, 'rb') as encrypted_file:
        if check_file_integrity(request, saved_hash_path, file.file.path):
            return redirect('home')
        encrypted_content = encrypted_file.read()

    decrypted_content = cipher_suite.decrypt(encrypted_content)

    # Create a temporary file for the decrypted content
    temp_file_path = os.path.join(path, 'temp_decrypted_file.txt')
    with open(temp_file_path, 'wb') as temp_file:
        temp_file.write(decrypted_content)

    # Serve the decrypted content as a response for download
    with open(temp_file_path, 'rb') as temp_file:
        response = HttpResponse(temp_file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{file.file.name}"'

    # Remove the temporary decrypted file
    os.remove(temp_file_path)

    return response


@my_login_required()
def share_file(request, file_id):
    """
    Handles file sharing.

    Args:
        request (HttpRequest): The request object.
        file_id (int): The ID of the file to be shared.

    Returns:
        HttpResponse: The response object.
    """
    if request.method == 'POST':
        try:  # Try to get the FileTransfer object with the given file_id.
            file = get_object_or_404(FileTransfer, id=file_id)
        except:
            messages.error(request, "File doesn't exist.")
            return redirect('home')

        username = request.POST.get('username')  # Get the username from the form data.

        if request.user != file.uploader:
            messages.error(request, "You cannot share files that you did not upload.")
            return redirect('home')

        if not User.objects.filter(username=username):
            messages.error(request, f"Username '{username}' doesn't exist.")
            return redirect('upload_file')
        user = get_object_or_404(User, username=username)

        # Check if the user already has access to the file.
        if user in file.shared_with.all():
            messages.error(request, "User already has access to the file.")
            return redirect('upload_file')
        file.shared_with.add(user)  # Add the user to the list of users with access to the file.

        messages.success(request,
                         f"'{file.title}' has been successfully shared.")  # Display a success message and redirect to the upload_file page.
        return redirect('upload_file')


@my_login_required()
def remove_file(request, file_id):
    """
    Handles file removal.

    Args:
        request (HttpRequest): The request object.
        file_id (int): The ID of the file to be removed.

    Returns:
        HttpResponse: The response object.
    """
    try:
        # Try to get the FileTransfer object with the given file_id.
        file = get_object_or_404(FileTransfer, id=file_id)

    except:
        # If the file doesn't exist, display an error message and redirect to the home page.
        messages.error(request, "File doesn't exist.")
        return redirect('home')
    # give an error message if a user tries to delete a file they did not upload
    if request.user != file.uploader:
        messages.error(request, "You cannot delete files that you did not upload.")
        return redirect('home')

    file.delete()
    os.remove(file.file.path)
    messages.success(request, f"You have successfully removed '{file.title}'.")
    return redirect('upload_file')


def get_key(request):
    """
    Retrieves the encryption key.

    Args:
        request (HttpRequest): The request object.

    Returns:
        bytes: The encryption key.
    """
    path = os.path.dirname(__file__)  # Get the directory path of the current file (in current directory).
    key_file_path = os.path.join(path, 'encryption_key.key')

    try:
        with open(key_file_path, 'rb') as key_file:
            key = key_file.read()

    except:
        # If there's an error, display an error message and redirect to the upload page.
        messages.error(request, "Error uploading file, key doesn't exist.")
        return redirect('upload')

    return key
