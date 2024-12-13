from django.shortcuts import render
from django.contrib import messages
from users.models import UserRegistrationModel, UserImagePredictinModel
from .utility.AlgorithmExecutions import KNNclassifier
from django.http import JsonResponse
from itertools import groupby
from operator import itemgetter
from datetime import datetime
from collections import Counter



# Create your views here.

def AdminLoginCheck(request):
    if request.method == 'POST':
        usrid = request.POST.get('loginid')
        pswd = request.POST.get('pswd')
        print("User ID is = ", usrid)
        if usrid == 'admin' and pswd == 'admin':
            return render(request, 'admins/AdminHome.html')
        elif usrid == 'Admin' and pswd == 'Admin':
            return render(request, 'admins/AdminHome.html')
        else:
            messages.success(request, 'Please Check Your Login Details')
    return render(request, 'AdminLogin.html', {})


def AdminHome(request):
    return render(request, 'admins/AdminHome.html')


def ViewRegisteredUsers(request):
    data = UserRegistrationModel.objects.all()
    return render(request, 'admins/RegisteredUsers.html', {'data': data})


def AdminActivaUsers(request):
    if request.method == 'GET':
        id = request.GET.get('uid')
        status = 'activated'
        print("PID = ", id, status)
        UserRegistrationModel.objects.filter(id=id).update(status=status)
        data = UserRegistrationModel.objects.all()
        return render(request, 'admins/RegisteredUsers.html', {'data': data})





def AdminStressDetected(request):
    # Fetch data from the database and order it by username and cdate
    data = UserImagePredictinModel.objects.all().order_by('username', 'cdate')
    user_data = list(data.values('id', 'username', 'filename', 'emotions', 'cdate', 'file'))

    # Extract only the date from cdate (ignoring the time)
    for item in user_data:
        item['cdate_only'] = item['cdate'].date()

    # Grouping logic
    final_data = {}
    for username, user_entries in groupby(user_data, key=itemgetter('username')):
        sorted_entries = sorted(user_entries, key=lambda x: x['cdate_only'])  # Sort by date
        user_grouped_by_date = {}
        
        for date, entries in groupby(sorted_entries, key=lambda x: x['cdate_only']):
            entries_list = list(entries)
            
            # Count stress statuses for the date
            status_counts = Counter()
            for entry in entries_list:
                if 'In Stress' in entry['emotions']:
                    status_counts['In Stress'] += 1
                elif 'Not in Stress' in entry['emotions']:
                    status_counts['Not in Stress'] += 1
            
            # Determine the overall stress status for the date
            if status_counts['In Stress'] > status_counts['Not in Stress']:
                stress_status = 'In Stress'
            elif status_counts['In Stress'] < status_counts['Not in Stress']:
                stress_status = 'Not in Stress'
            else:
                stress_status = 'Neutral'
            
            # Save the data for the template
            user_grouped_by_date[date] = {
                'entries': entries_list,
                'stress_status': stress_status
            }
        
        # Save the grouped data for the user
        final_data[username] = user_grouped_by_date
    
    # Prepare the context for rendering
    context = {
        'data': final_data  # Pass grouped data by user and date to the template
    }
    
    return render(request, 'admins/AllUsersStressView.html', context)




def AdminKNNResults(request):
    obj = KNNclassifier()
    df, accuracy, classificationerror, sensitivity, Specificity, fsp, precision = obj.getKnnResults()
    df.rename(
        columns={'Target': 'Target', 'ECG(mV)': 'Time pressure', 'EMG(mV)': 'Interruption', 'Foot GSR(mV)': 'Stress',
                 'Hand GSR(mV)': 'Physical Demand', 'HR(bpm)': 'Performance', 'RESP(mV)': 'Frustration', },
        inplace=True)
    data = df.to_html()
    return render(request, 'admins/AdminKnnResults.html',
                  {'data': data, 'accuracy': accuracy, 'classificationerror': classificationerror,
                   'sensitivity': sensitivity, "Specificity": Specificity, 'fsp': fsp, 'precision': precision})
