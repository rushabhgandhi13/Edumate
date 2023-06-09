import calendar
from datetime import date
from datetime import datetime, timedelta
import cv2
from django.shortcuts import get_object_or_404, render
import string, random
from django.http import FileResponse, Http404, HttpResponseRedirect, StreamingHttpResponse
from django.urls import reverse

from Edumate_app.models import Students, Teachers
from Student.models import ClassStudents, SubmittedAssignments, PeerStudents, Attendance, Quiz_marks
from Teacher.forms import EventForm
from .models import *
import random
import copy
from django.shortcuts import redirect, render

from django.views import generic
from django.utils.safestring import mark_safe
from .utils import Calendar, gen_bounding_boxes

from django.contrib import messages

from PyPDF2 import PdfReader
import os
from sklearn.metrics.pairwise import cosine_similarity        # function to measure similarity between two vectors
import re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer
import numpy as np
from huggingface_hub import from_pretrained_keras
from keras.models import load_model
from django.http import JsonResponse
from django.utils.dateparse import parse_datetime
from json import dumps


capture = 0
frame = None

# Create your views here.
similarity_sentence_transformer_model = SentenceTransformer('all-MiniLM-L6-v2')
model = load_model(os.path.join('./Teacher/static/Teacher',"model.h5"))

def teach_home(request, pk):
    teacher_c = Teachers.objects.get(teach_id=pk)
    class_data = ClassTeachers.objects.filter(teach_id=pk)
    studs=[]
    for i in class_data:
        studs.append(len(ClassStudents.objects.filter(class_code=i.class_code)))
    
    if(request.method=="POST"):
        class_room=ClassTeachers()
        class_room.teach_id=pk
        class_room.class_name=request.POST.get('name')
        class_room.class_code=str(''.join(random.choices(string.ascii_uppercase + string.digits, k = 6)))
        class_room.save() 
        return render(request, 'Teacher/teacher_home.html', {'class_data': zip(class_data, studs), 'teacher': teacher_c, 'pk': pk})
    
    return render(request, 'Teacher/teacher_home.html', {'class_data': zip(class_data, studs), 'teacher': teacher_c, 'pk': pk})

def deleteclass(request, pk):
    if request.method == "POST":
        ClassTeachers.objects.get(class_code=request.POST['class_code']).delete()
        return JsonResponse({'info': 'succ'})

def classroom(request, pk, pk2):
    context={'pk': pk, 'pk2': pk}
    if(request.method=="POST"):
        assignment=Assignments()
        assignment.assignment_name=request.POST.get('name')
        assignment.assignment_description=request.POST.get('description')
        assignment.class_code=pk2
        assignment.max_marks=request.POST.get('marks')
        assignment.duedate=request.POST.get('duedate')
        if request.POST.get('peer')=="on":
            assignment.peer_grade=True
        else:
            assignment.peer_grade=False
        print(request.POST.get('peer'))
        assignment.save()
    a=Assignments.objects.filter(class_code=pk2)
    assign = []
    studs=[]
    class_data = ClassTeachers.objects.filter(teach_id=pk)
    for i in class_data:
        studs.append(len(ClassStudents.objects.filter(class_code=i.class_code)))
    totalStudents = studs[0]
    studs = []
    for i in a:
        s = SubmittedAssignments.objects.filter(assignment_id=i.assignment_id)
        assign.append([i, len(s)])
        studs.append(totalStudents-len(s))
    total_studs_value=len(ClassStudents.objects.filter(class_code=pk2))
    return render(request, 'Teacher/classroom.html', {'assign': zip(assign, studs), 'pk': pk, 'pk2': pk2, 'total': total_studs_value})

def assignmentsub(request, pk, pk2, pk3):
    submitted=SubmittedAssignments.objects.filter(assignment_id=pk3)
    stud_names=[]
    # for i in submitted:
    #     stud_names.append(Students.object.get(stud_id=i.stud_id).name)
    peerassign=PeerStudents.objects.filter(assign_id=pk3)
    assign_grade=Assignments.objects.filter(assignment_id =pk3)
    assign_flag=assign_grade[0].peer_grade
    sorterval=[]
    for i in submitted:
        received1=PeerStudents.objects.filter(assign_id=pk3, as_peer_1=i.stud_id)
        received2=PeerStudents.objects.filter(assign_id=pk3, as_peer_2=i.stud_id)
        temp=[i.stud_id]
        for j in received1:
            temp.append(j.stud_id)
            temp.append(j.as_1_marks)
        for j in received2:
            temp.append(j.stud_id)
            temp.append(j.as_2_marks)
        sorterval.append(temp)
    if(request.method=="POST"):
        sub_stud=SubmittedAssignments.objects.filter(assignment_id=pk3)
        studs=ClassStudents.objects.filter(class_code=pk2)
        if(len(sub_stud)!=len(studs)):
            print("Some students are still left to submit their assignments")
        else:
            a=[]
            stud_sub=[]
            for i in sub_stud:
                a.append(i.assign_id)
                stud_sub.append(i.stud_id)
            b=copy.deepcopy(a)
            random.shuffle(a)
            a=a+a
            ans=[]
            j=0
            for i in range(0, len(b)):
                while(a[j]==b[i] or a[j]=="X"):
                    j=(j+1)%len(a)
                ans.append([a[j]])
                a[j]="X"
                while(a[j]==b[i] or ans[i][0]==a[j] or a[j]=="X"):
                    j=(j+1)%len(a)
                ans[i].append(a[j])
                a[j]="X"
            for i in range(0,len(stud_sub)):
                peer=PeerGrade()
                peer.stud_id=stud_sub[i]
                peer.assign_id=pk3
                peer.peer_1=ans[i][0]
                peer.peer_2=ans[i][1]
                peer.save()
    return render(request, 'Teacher/show_assignments.html', {'submit': submitted, 'pk': pk, 'pk2': pk2 ,'pk3': pk3, "peer": peerassign, "shr": sorterval, 'peerf': assign_flag})

def assignmentgrade(request, pk, pk2, pk3,pk4):
    submitted=SubmittedAssignments.objects.get(assignment_id=pk3,stud_id = pk4)
    assignment=Assignments.objects.get(assignment_id=pk3)
    stud = Students.objects.get(stud_id = pk4)
    file_url = "http://127.0.0.1:8000"+submitted.assign_file.url
    if request.method=="POST":
        if(float(request.POST.get('marks')) < float(assignment.max_marks)):
            submitted.marks=request.POST.get('marks')
            submitted.save()
            messages.error(request, "Marks updated successfully")
            return redirect('grade', pk=pk, pk2=pk2, pk3=pk3, pk4=pk4)
        else:
            messages.error(request, "Marks cant be greater than maximum marks")
            return redirect('grade', pk=pk, pk2=pk2, pk3=pk3, pk4=pk4)
    return render(request, 'Teacher/grade_assignments.html', {'student_name':stud.name,'file':file_url,'submit': submitted, 'pk': pk, 'pk2': pk2, 'pk3': pk3,'assign': assignment})

def announcement(request, pk, pk2):
    if (request.method == 'POST'):
        announcement = Announcements()
        announcement.announce_data = request.POST.get('announce_data')
        announcement.teach_id = pk
        announcement.class_code = pk2
        # print(announcement.announce_data, announcement.teach_id, announcement.class_code)
        announcement.save()
    announcement_data = Announcements.objects.filter(class_code = pk2).order_by('-date')
    return render(request, 'Teacher/announcement_teach.html', {'pk': pk, 'pk2': pk2, 'announcement_data': announcement_data})

def ann_delete(request, pk, pk2, id):
    delAnnouncement = Announcements.objects.get(id=id)
    delAnnouncement.delete()
    return redirect('announcementteach', pk=pk, pk2=pk2)

class schedule(generic.ListView):
    model = Schedule
    template_name = 'Teacher/schedule.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        d = get_date(self.request.GET.get('month', None))
        pk1 = self.kwargs['pk']
        classcode = self.kwargs['pk2']
        cal = Calendar(d.year, d.month, classcode)
        html_cal = cal.formatmonth(withyear=True)
        context['calendar'] = mark_safe(html_cal)
        context['prev_month'] = prev_month(d)
        context['next_month'] = next_month(d)
        context['pk2'] = classcode
        context['pk1'] = pk1
        # context['pk'] = pk1
        return context

def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()

def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month

def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month

def event(request,pk, pk2, id=None):
    instance = Schedule()
    if id:
        instance = get_object_or_404(Schedule, pk=id)
    else:
        instance = Schedule()
    
    form = EventForm(request.POST or None, instance=instance)
    if request.POST and form.is_valid():

        eform = form.save(commit = False)
        eform.teach_id = pk
        eform.class_code = pk2
        eform.save()
        return HttpResponseRedirect(reverse('schedule', args=(instance.teach_id,instance.class_code)))
    return render(request, 'Teacher/event.html', {'form': form,'pk1':pk,'pk2':pk2, 'pk': pk})

def create_quiz(request, pk, pk2):
    '''
    Function to create quiz for a particular classroom with id = pk2
    rdc = number of options per question
    Data Sent to DB = {
        pk [teacher id],
        pk2 [classroom id / classCode],
        Quiz Name,
        Quiz Time,
        Question + Answer [for all the questions in the quiz] --> multiple values for single quiz,
    }
    '''   
    if request.POST:

        quizName = request.POST.get('quiz_name')
        quizdate = request.POST.get('quiz_date')
        quizTime = request.POST.get('quiz_time')
        count = request.POST.get('question_count')
        description = request.POST.get('desc')
        c = request.POST.get('radio_count')
        rdc = request.POST.get('rdc')
        rdc = rdc.split(",")
        finalRdc = []
        for i in range(0, len(rdc)-1, 2):
            finalRdc.append([rdc[i], rdc[i+1]])
        print(f"Finalrdc : {finalRdc}")
        secondValues = []
        for i in range(len(finalRdc)):
            secondValues.append(finalRdc[i][1])
        count, c = int(count), int(c)
        allRadioButtonState = []
        questions = []
        options = []
        correctOP = []
        print("secondvalue: " + str(secondValues))
        for i in finalRdc:
            val = request.POST.get('question' + i[0])
            questions.append(val)
            # op = request.POST.getlist('option'+ i[0])
            # options.append(op)
            temp = []
            opTemp = []
            radioTemp = []
            for j in range(1, int(i[1])+1):
                op = request.POST.get('option'+ i[0] + str(j))
                opTemp.append(op)
                rd = request.POST.get('acoption'+ i[0] + str(j))
                if rd == 'on':
                    temp.append(j)
                radioTemp.append(rd)
            options.append(opTemp)
            allRadioButtonState.append(radioTemp)
            correctOP.append(temp)
        # print(quizName)
        # print(quizTime)
        # print(allRadioButtonState)
        # print(questions)
        # print(options)
        # print(correctOP)
        quiz_object = Quiz(quiz_name = quizName, description = description, time_limit = quizTime,quiz_date = quizdate, teach_id = pk, class_code = pk2)
        quiz_object.save()
        markForEachQuestion = 1

        

        for i in range(len(questions)):
            question_object = Question(quiz = quiz_object, question_name = questions[i], marks = markForEachQuestion)
            question_object.save()

            img = request.FILES.getlist('question_img' + str(i+1))
            for j in img:
                img_object = QuestionImage(question = question_object, image = j)
                img_object.save()
            
            k = 0
            for j in options[i]:
                if k+1 in correctOP[i]:
                    # if correctOP[i][0]-1 == options[i].index(j):
                    option_object = Options(question = question_object, option_name = j, correct = True)
                    option_object.save()
                else:
                    option_object = Options(question = question_object, option_name = j, correct = False)
                    option_object.save()
                k += 1
        
    allQuiz = Quiz.objects.filter(teach_id = pk, class_code = pk2)

    return render(request, 'Teacher/createQuiz.html', {'pk': pk, 'pk2': pk2, 'allQuiz': allQuiz})


def attendance(request, pk, pk2):
    global model
    all_att = Attendance.objects.filter(teacher_id=pk, class_id=pk2).order_by('-att_id')
    nums_studs_present=[]
    attdates=[]
    total_num = len(ClassStudents.objects.filter(class_code=pk2))
    for i in all_att:
        date_single = parse_datetime(i.start_time)
        attdates.append(date_single)
        single_num = len(AttStud.objects.filter(att_id=i.att_id))
        percent = (single_num / total_num) * 100
        nums_studs_present.append([single_num, percent])
    if request.method=="POST":
        new_att=Attendance()
        new_att.teacher_id=pk
        new_att.class_id=pk2
        new_att.start_time=request.POST.get('atttimes')
        new_att.end_time=request.POST.get('atttimee')
        new_att.code=str(''.join(random.choices(string.ascii_uppercase + string.digits, k = 6)))
        new_att.save()
        att_list = request.FILES.getlist('attimg')
        for i in att_list:
            attimg = Attendance_images()
            attimg.att_id = new_att
            attimg.att_image = i
            attimg.save()
            
            temp_i = str(i)
            gen_bounding_boxes(temp_i,model)
        

        messages.success(request, 'Attendance created and code is = '+new_att.code)
        return redirect('attendance', pk=pk, pk2=pk2)
    return render(request, 'Teacher/attendance.html', {'pk': pk, 'pk2': pk2, 'all_att': zip(all_att, attdates, nums_studs_present)})

def video_feed(request, pk):
    return StreamingHttpResponse(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    camera = cv2.VideoCapture(0)

    global capture,frame
    while True:
        success, frame = camera.read()
        if success:
            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame,1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                
            except Exception as e:
                pass
        else:
            pass       

def view_att(request, pk, pk2, pk3):
    all_att_id=AttStud.objects.filter(att_id=pk3)
    all_att=[]
    all_studs=ClassStudents.objects.filter(class_code=pk2)
    att_ids=[]
    for i in all_att_id:
        val={}
        val['name']=i.stud_id.name
        val['time']=i.att_time
        val['att_id']=i.att_id.att_id
        val['stud_id']=i.stud_id.stud_id
        att_ids.append(i.stud_id.stud_id)
        all_att.append(val)
    stud_ids=[]
    for i in all_studs:
        stud_ids.append(i.stud_id)
    all_stud_names_ids=[]
    for i in stud_ids:
        if i not in att_ids:
            try:
                stud=Students.objects.get(stud_id=i)
                single_stud={'stud_id': i, 'name': stud.name}
                all_stud_names_ids.append(single_stud)
            except:
                continue
    print(all_stud_names_ids)
    if request.method == "POST":
        if 'student_id' in request.POST:
            if request.POST['student_id']=="none":
                messages.error(request, "Please select a valid option")
                return redirect('viewatt', pk=pk, pk2=pk2, pk3=pk3)
            tem=request.POST['student_id'].split("(")
            tem=tem[-1]
            tem=tem.split(")")
            att=AttStud()
            att.att_id=Attendance.objects.get(att_id=pk3)
            att.stud_id=Students.objects.get(stud_id=int(tem[0]))
            att.att_time=str(datetime.now())
            att.img_number=-1
            att.save()
            return redirect('viewatt', pk=pk, pk2=pk2, pk3=pk3)
        AttStud.objects.get(att_id=request.POST['att_id'], stud_id=request.POST['stud_id']).delete()
        messages.error(request, "Deleted successfully")
        return redirect('viewatt', pk=pk, pk2=pk2, pk3=pk3)
    return render(request, 'Teacher/view_att.html', {'pk': pk, 'pk2': pk2, 'pk3': pk3, 'all_att': all_att, 'all_stud': all_stud_names_ids})

def quiz_info(request, pk, pk2, pk3):
    quiz = Quiz.objects.get(id = pk3)
    quiz_responses = Quiz_marks.objects.filter(quiz = quiz)
    return render(request, 'Teacher/individual_quiz.html', {'pk': pk, 'pk2': pk2, 'pk3': pk3, 'quiz_responses': quiz_responses})

def assignmentSimilarityCheck(request, pk, pk2, pk3):
    global similarity_sentence_transformer_model
    assignments = SubmittedAssignments.objects.filter(assignment_id=pk3)
    data = []
    for i in assignments:
        student = Students.objects.filter(stud_id=i.stud_id)
        data.append([i, student])

    all_assignments = SubmittedAssignments.objects.filter(assignment_id = pk3)
    files = []
    students = []
    for i in all_assignments:
        files.append(i.assign_file.url)
        students.append(i.stud_id)
    # files_text = getTextFromPDF(files)
    # embeddings = similarity_sentence_transformer_model.encode(files_text)
    # similarities = predict_similarity(embeddings,students)
    # # print(similarities)
    # for j in similarities:
    #     # print(j)
    #     plag = Plagarism()
    #     plag.assignment_id = Assignments.objects.get(assignment_id = pk3)
    #     plag.percentage_similarity = j['similarity_score']
    #     plag.stud_assignment1 = SubmittedAssignments.objects.get(stud_id=j['stud_1'], assignment_id=pk3)
    #     plag.stud_assignment2 = SubmittedAssignments.objects.get(stud_id=j['stud_2'], assignment_id=pk3)
    #     plag.save()
    # print(data)
    # ,percentage_similarity__range=(0.5, 1)
    plag = Plagarism.objects.filter(assignment_id = pk3).order_by('-percentage_similarity')
    # print("ABCD_-_Plag")
    # print(plag)
    return render(request, 'Teacher/assignmentSimilarityCheck.html', {'pk': pk, 'pk2': pk2, 'pk3': pk3, 'assignments': data, 'plagData': plag})

def preprocess_text(text):
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove non-alphabetic characters and other special characters
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Convert the text to lowercase
    text = text.lower()
    
    # Remove extra whitespaces
    text = re.sub(r'\s+', ' ', text)
    
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Remove stop words
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    # Join the tokens back into a string
    preprocessed_text = ' '.join(tokens)
    
    return preprocessed_text

def getTextFromPDF(files):
    data = []
    for f in files:
        # print(f)
        reader = PdfReader("." + f)

        header = os.path.commonprefix([i.extract_text() for i in reader.pages])
        pages = []

        for i in reader.pages:
            pages.append(preprocess_text(i.extract_text()[len(header):]))

        text = ' '.join(pages)
        data.append(text)

    return data

def predict_similarity(embeddings,students):
    similarities = []
    for i in range(len(embeddings)):
        for j in range(len(embeddings)):
            if i>=j:
                continue
            score = float(cosine_similarity(np.expand_dims(embeddings[i],axis=0),np.expand_dims(embeddings[j],axis=0))[0][0])
            similarities.append({'stud_1':students[i],'stud_2':students[j],'similarity_score':score})
            # similarities.append({'stud_1':students[j],'stud_2':students[i],'similarity_score':score})
    return similarities
    
def logout(request, pk):
    request.session.flush()
    return redirect('home')
