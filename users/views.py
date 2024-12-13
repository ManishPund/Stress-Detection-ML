from django.shortcuts import render, redirect, HttpResponse
from .forms import UserRegistrationForm
from .models import UserRegistrationModel,UserImagePredictinModel
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .utility.GetImageStressDetection import ImageExpressionDetect
from .utility.MyClassifier import KNNclassifier
from subprocess import Popen, PIPE
import subprocess
from itertools import groupby
from operator import itemgetter
from datetime import datetime
from collections import Counter
# Create your views here.


# Create your views here.
from django.db import IntegrityError
from django.contrib import messages

def UserRegisterActions(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                print('Data is Valid')
                form.save()
                messages.success(request, 'You have been successfully registered. Please wait for admin approval.')
                form = UserRegistrationForm()  # Reset form after success
            except IntegrityError:
                messages.error(request, 'There was an error processing your registration. Try again.')
        else:
            # Display form validation errors
            print("Form is invalid. Errors:", form.errors)
            # Optionally, you can display the errors in the template as well:
            messages.error(request, f"Form is invalid: {form.errors.as_text()}")
    else:
        form = UserRegistrationForm()

    return render(request, 'UserRegistrations.html', {'form': form})




def UserLoginCheck(request):
    if request.method == "POST":
        loginid = request.POST.get('loginname')
        pswd = request.POST.get('pswd')
        print("Login ID = ", loginid, ' Password = ', pswd)
        try:
            check = UserRegistrationModel.objects.get(loginid=loginid, password=pswd)
            status = check.status
            print('Status is = ', status)
            if status == "activated":
                request.session['id'] = check.id
                request.session['loggeduser'] = check.name
                request.session['loginid'] = loginid
                request.session['email'] = check.email
                print("User id At", check.id, status)
                return render(request, 'users/UserHome.html', {})
            else:
                messages.success(request, 'Your Account Not at activated')
                return render(request, 'UserLogin.html')
        except Exception as e:
            print('Exception is ', str(e))
            pass
        messages.success(request, 'Invalid Login id and password')
    return render(request, 'UserLogin.html', {})


def UserHome(request):
    return render(request, 'users/UserHome.html', {})

# Image Upload View
def UploadImageForm(request):
    loginid = request.session['loginid']
    return render(request, 'users/UserImageUploadForm.html')

def UploadImageAction(request):
    if request.method == "POST" and request.FILES['file']:
        image_file = request.FILES['file']

        # Ensure it is a JPG file
        if not image_file.name.endswith('.jpg'):
            messages.error(request, 'THIS IS NOT A JPG FILE')
            return render(request, 'users/UserImageUploadForm.html')

        fs = FileSystemStorage()
        filename = fs.save(image_file.name, image_file)
        uploaded_file_url = fs.url(filename)

        # Get emotion prediction using ImageExpressionDetect
        obj = ImageExpressionDetect()
        emotion = obj.getExpression(filename)

        # Save image info to the database
        username = request.session['loggeduser']
        loginid = request.session['loginid']
        email = request.session['email']
        UserImagePredictinModel.objects.create(username=username, email=email, loginid=loginid, filename=filename, emotions=emotion, file=uploaded_file_url)

        return render(request, 'users/UserImageUploadForm.html', {'message': 'Image uploaded successfully!'})
    
    return render(request, 'users/UserImageUploadForm.html')

# Results Table View



def ResultsTable(request):
    loginid = request.session.get('loginid')
    if not loginid:
        messages.error(request, 'Session expired. Please log in again.')
        return redirect('UserLogin')  # Replace with your login URL

    # Fetch data for the logged-in user
    data = UserImagePredictinModel.objects.filter(loginid=loginid)

    # Sort the data by 'cdate' (using only the date part)
    sorted_data = sorted(data, key=lambda x: x.cdate.date())  # .date() extracts only the date part

    # Group the sorted data by 'cdate' (again, using only the date part)
    grouped_data = {}
    for date, entries in groupby(sorted_data, key=lambda x: x.cdate.date()):
        entries_list = list(entries)
        
        # Count stress statuses
        status_counts = Counter()
        for entry in entries_list:
            if 'In Stress' in entry.emotions:
                status_counts['In Stress'] += 1
            elif 'Not in Stress' in entry.emotions:
                status_counts['Not in Stress'] += 1

        # Determine overall status for the date
        if status_counts['In Stress'] > status_counts['Not in Stress']:
            stress_status = 'In Stress'
        elif status_counts['In Stress'] < status_counts['Not in Stress']:
            stress_status = 'Not in Stress'
        else:
            stress_status = 'Neutral'

        # Save the data for the template
        grouped_data[date] = {
            'entries': entries_list,
            'stress_status': stress_status
        }

    return render(request, 'users/UserResult.html', {'grouped_data': grouped_data})


# Views for other functionalities (unchanged)


def UserEmotionsDetect(request):
    if request.method=='GET':
        imgname = request.GET.get('imgname')
        obj = ImageExpressionDetect()
        emotion = obj.getExpression(imgname)
        loginid = request.session['loginid']
        data = UserImagePredictinModel.objects.filter(loginid=loginid)
        return render(request, 'users/UserResult.html', {'data': data})

def UserLiveCameDetect(request):
    obj = ImageExpressionDetect()
    obj.getLiveDetect(request)
    return render(request, 'users/UserLiveHome.html', {})


def UserKerasModel(request):
    # p = Popen(["python", "kerasmodel.py --mode display"], cwd='StressDetection', stdout=PIPE, stderr=PIPE)
    # out, err = p.communicate()
    subprocess.call("python kerasmodel.py --mode display")
    return render(request, 'users/UserLiveHome.html', {})

def UserKnnResults(request):
    obj = KNNclassifier()
    df,accuracy,classificationerror,sensitivity,Specificity,fsp,precision = obj.getKnnResults()
    df.rename(columns={'Target': 'Target', 'ECG(mV)': 'Time pressure', 'EMG(mV)': 'Interruption', 'Foot GSR(mV)': 'Stress', 'Hand GSR(mV)': 'Physical Demand', 'HR(bpm)': 'Performance', 'RESP(mV)': 'Frustration', }, inplace=True)
    data = df.to_html()
    return render(request,'users/UserKnnResults.html',{'data':data,'accuracy':accuracy,'classificationerror':classificationerror,
                                                       'sensitivity':sensitivity,"Specificity":Specificity,'fsp':fsp,'precision':precision})

