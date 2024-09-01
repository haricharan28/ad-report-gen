from django.shortcuts import render, redirect
from django.contrib import messages
import MySQLdb as sql
from .models import clientdetails, logindetails, requirements, user_report

from django.db.models import Q
import ast
import json

# Create your views here.
#sql connection
def sqlconn():
    conn=sql.connect(user='root', db='marketing', passwd='RooT@2801')
    cur=conn.cursor()
    return cur, conn

def login(request):
    global clientid, clientname
    print(request.POST.get('username'))
    print(request.POST.get('password'))
    username=request.POST.get('username')
    password=request.POST.get('password')
    print("request", request.method)
    if(request.method=='GET'):
        return render(request, 'login.html')
    else:
        q="select * from market_logindetails where binary username='{}' and binary password='{}'".format(username, password)
        cur, conn = sqlconn()
        cur.execute(q)
        data=list(cur.fetchall())
        print(data)
        if(len(data)==0):
            print("Login Unsuccessful")
            messages.success(request, "Invalid Details!")
            return render(request, 'login.html')
        else:
            print("Login Successful")
            role=data[0][-1]
            if(role=="superadmin"):
                print("superadmin")
                return render(request, 'SAdmin_Homepage.html')
            elif(role=="user"):
                print("user")
                return render(request, 'User_Homepage.html')
            elif(role=="client"):
                print("client")
                dsig = clientdetails.objects.filter(username=username)
                #print(dsig)
                for i in dsig:
                    dsg=i.role 
                    if dsg =='client':
                        #print(i.id)
                        clientname = i.clientname
                        clientid = i.id
                        cl_id = 'select id from market_requirements where deptid_id = {}'.format(clientid)
                        cur.execute(cl_id)
                        clientid = cur.fetchone()[0]
                        #print(clientid)
                        conn.commit()
                        q = "select distinct campaign_name from  market_user_report where clientname = '{}'".format(i.clientname)
                        cur.execute(q)
                        campaigns = list(cur.fetchall())
                        ##print(campaigns[0][0],campaigns[0])
                        ##campaigns=user_report.objects.filter(clientid_id = i.id).distinct()
                        cl_access_q = f"select sel_options, client_access from market_requirements where id={clientid} and campaign_name='{campaigns[0][0]}';"
                        #print(cl_access_q)
                        cur.execute(cl_access_q)
                        data=cur.fetchone()
                        #print(ast.literal_eval(data[0]), ast.literal_eval(data[1]))
                        op= ast.literal_eval(data[0])
                        cl_access_col = ast.literal_eval(data[1])
                        head = ['market_user_report.id', 'clientname', 'market_user_report.campaign_name', 'date', 'no_of_impressions', 'no_of_clicks', 'no_of_sessions', 'cpm', 'cpc', 'cps', 'total_cpm', 'total_cpc', 'total_cps', 'market_user_report.ctr', 'clientid_id']
                        col=head[:4]
                        print('ass',cl_access_col)
                        for i in head:
                            if i in cl_access_col:
                                col.append(i)            
                        #print(col)               
                       
                        camp_data_query=f"select {', '.join(col)} from market_user_report where clientid_id={clientid} and campaign_name='{campaigns[0][0]}' order by date desc;"
                        #print(camp_data_query)
                        cur.execute(camp_data_query)
                        camp_data = cur.fetchall()
                        #print(camp_data)
                        headers = [i[0] for i in cur.description]
                        print('col',headers)
                       
                        f_camp_data = list(map(lambda x:{'id':x[0],'values':list(x[1:])},camp_data))
                        campaign = user_report.objects.filter(campaign_name=campaigns[0][0]).order_by('date')
                        #print(campaigns[0][0])
                        dates,fields,total=statics(op,clientname,campaigns[0][0])
                        
                        #print(fields)
                        
                        #print(fields['no_of_sessions'])
                        #report,dates,no_impre,no_clicks = statics(campaigns[0][0])
                        #return render(request, 'campaign.html',{'campaign':campaign,'campaigns':campaigns,'client':clientname,'data':report,'dates':dates,'impr':no_impre,'clicks':no_clicks, 'camp':campaigns[0][0]})
                        return render(request, 'campaign.html',{'camp_data':json.dumps(f_camp_data),'camp_col':json.dumps(headers[1:]),'campaign':campaign,'campaigns':campaigns,'client':clientname,'camp':campaigns[0][0],'dates':json.dumps(dates),'fields':json.dumps(fields),'total':json.dumps(total)})
                return render(request, 'clientpage.html')
            else:
                messages.success(request, "Invalid Details!")
                return render(request, 'login.html')

###------###------###------###------ FOR CLIENT PAGE ###------###------###------###------###------###------###------###------###------###------

def statics(op,cl_name,camp):
    cur,conn = sqlconn()
    '''
    print(camp)
    cur,conn = sqlconn()
    q = "select * from  market_user_report where campaign_name = '{}' order by date".format(camp)
    cur.execute(q)
    conn.commit()
    data =  list(cur.fetchall())
    sum_impressions = 0
    sum_clicks = 0
    total_cost_impr = 0
    total_cost_click = 0
    total_total_cost,ctr = 0
    dates= []
    no_impre =[]
    no_clicks =[]
    for i in data:
        dates.append(i[3])
        no_impre.append(i[4])
        no_clicks.append(i[5])
        i=list(i)[4:]
        sum_impressions += i[0]
        sum_clicks +=i[1]
        total_cost_impr +=i[4]
        total_cost_click +=i[5]
        total_cost =i[6]
    report=[sum_impressions,sum_clicks,total_cost]
    return (report, dates, no_impre,no_clicks)
    '''
    #print(op)
    #print(data)
    field={}
    total={}
    dates=None
    no_impre=None
    no_clicks=None
    no_sessions=None
    if len(op)!=0:
        cur.execute(f"select date from market_user_report where clientname='{cl_name}' and campaign_name='{camp}'")
        d= cur.fetchall()
        #print(d)
        dates=list(map(lambda x:x[0],d))
        for i in op:
            if i=='impressions':
                cur.execute(f"select no_of_impressions from market_user_report where clientname='{cl_name}' and campaign_name='{camp}'")
                d= cur.fetchall()
                #print(d)
                no_impre=list(map(lambda x:x[0],d))
                field['no_impre'] = no_impre
                total['Total Impressions'] = sum(no_impre)
                #print(no_impre)
            elif i=='clicks':
                cur.execute(f"select no_of_clicks from market_user_report where clientname='{cl_name}' and campaign_name='{camp}'")
                d= cur.fetchall()
                #print(d)
                no_clicks=list(map(lambda x:x[0],d))
                field['no_clicks'] = no_clicks
                total['Total Clicks'] = sum(no_clicks)
            elif i=='session':
                cur.execute(f"select no_of_sessions from market_user_report where clientname='{cl_name}' and campaign_name='{camp}'")
                d= cur.fetchall()
                #print(d)
                no_sessions=list(map(lambda x:x[0],d))
                field['no_sessions'] = no_sessions
                total['Total Sessions'] = sum(no_sessions)
        
        

        #print('date:',dates)  
        #print('f:',field)
        return dates,field,total


            #field['impression']=cur.query(f"select no_of_impressions from market_user_report")

    

def campaign_details(request):
    print(request.GET)
    global clientname
    #print('client',clientid)
    cur,conn = sqlconn()
    #print(clientid)
    q = "select distinct campaign_name from  market_user_report where clientname = '{}'".format(clientname)
    cur.execute(q)
    campaigns = list(cur.fetchall())
    print(campaigns)
    conn.commit()
    #q = 'select no_of_impressions, no_of_clicks,no_of_sessions campaign_name from  market_user_report where clientid_id = {}'.format(clientid)
    #cur.execute(q)
    #print(statics(clientid))
    #labels = ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange']
    if request.method == 'POST':
        print('POST',request.POST)
        clientname=request.POST.get('clientname')
        selected_campaign = request.POST.get('campaign_name')

        q = "select distinct campaign_name from  market_user_report where clientname = '{}'".format(clientname)
        cur.execute(q)
        campaigns = list(cur.fetchall())
        
        '''
        #print(selected_campaign)
        campaign = user_report.objects.filter(campaign_name=selected_campaign).order_by('date')
        #campaigns=user_report.objects.filter(clientid_id = clientid).distinct('campaign_name')
        #context = {'campaign': campaign,'campaigns':campaigns,'client':clientname}
        report,dates,no_impre,no_clicks = statics(selected_campaign)
        #print(report,cost,dates,no_impre)
        context = {'campaign': campaign,'campaigns':campaigns,'client':clientname,'data':report,'dates':dates,'impr':no_impre,'clicks':no_clicks,'camp':selected_campaign}
        return render(request, 'campaign.html', context)
        '''

        cl_access_q = f"select sel_options, client_access from market_requirements where name='{clientname}' and campaign_name='{selected_campaign}';"
        print(cl_access_q)
        cur.execute(cl_access_q)
        data=cur.fetchone()
        #print(ast.literal_eval(data[0]), ast.literal_eval(data[1]))
        op= ast.literal_eval(data[0])
        cl_access_col = ast.literal_eval(data[1])
        head = ['market_user_report.id', 'clientname', 'market_user_report.campaign_name', 'date', 'no_of_impressions', 'no_of_clicks', 'no_of_sessions', 'cpm', 'cpc', 'cps', 'total_cpm', 'total_cpc', 'total_cps', 'ctr', 'clientid_id']
        col=head[:4]
        #print(cl_access_col)
        for i in head:
            if i in cl_access_col:
                col.append(i)
                
        print(col)               
       
        camp_data_query=f"select {', '.join(col)} from market_user_report where clientname='{clientname}' and campaign_name='{selected_campaign}' order by date desc;"
        #print(camp_data_query)
        cur.execute(camp_data_query)
        camp_data = cur.fetchall()
                        #print(camp_data)
        headers = [i[0] for i in cur.description]
                        #print('col',headers)
                       
        f_camp_data = list(map(lambda x:{'id':x[0],'values':list(x[1:])},camp_data))
        print(f_camp_data)
        dates,fields,total=statics(op,clientname,selected_campaign)
                        
        print(total)
                        
                        #print(fields['no_of_sessions'])
                        #report,dates,no_impre,no_clicks = statics(campaigns[0][0])
                        #return render(request, 'campaign.html',{'campaign':campaign,'campaigns':campaigns,'client':clientname,'data':report,'dates':dates,'impr':no_impre,'clicks':no_clicks, 'camp':campaigns[0][0]})
        return render(request, 'campaign.html',{'camp_data':json.dumps(f_camp_data),'camp_col':json.dumps(headers[1:]),'campaigns':campaigns,'client':clientname,'camp':selected_campaign,'dates':json.dumps(dates),'fields':json.dumps(fields),'total':json.dumps(total)})



    else:
        #print(campaigns)
        #report,cost = statics(clientid)
        #campaigns=user_report.objects.filter(clientid_id = clientid).distinct('campaign_name')
        return render(request, 'campaign.html',{'campaigns':campaigns,'client':clientname})


###------###------###------###------ FOR CLIENT PAGE ###------###------###------###------###------###------###------###------###------###------
#superadmin homepage
def homepage(request):
    return redirect('homepage')
#user homepage
def userhomepage(request):
    return render(request, 'User_Homepage.html')
#client homepage
# def campaign_details(request):
#     return redirect('clienthomepage')

#for viewing client details
def viewclientdetails(request):
    people=clientdetails.objects.all()  
    return render(request, 'SAdmin_ViewClientDetails.html', {'people':people})

#for taking client data from client form SA
def get_client_data(request):
    if request.method=='GET':
        dat=clientdetails.objects.all().values()
        return render(request, 'SAdmin_ClientDetails.html', {'dat':dat})
    elif request.method=='POST':
        clientname=request.POST['clientname']
        # it checks client name is already registered or not
        if clientdetails.objects.filter(clientname=clientname).exists():
            messages.error(request, "Client name already registered!")
            return render(request, 'SAdmin_ClientDetails.html')
        else:
            data=dict()
            if request.method=='GET':
                return render(request, 'SAdmin_ClientDetails.html', data)
            files=request.FILES
            clientname=request.POST.get('clientname')
            username=request.POST.get('username')
            password=request.POST.get('password')
            email=request.POST.get('email')
            date=request.POST.get('date')
            image=files.get('image')
            if image is None:
                image='uploads/dummy.png'
            role='client'
            instance=clientdetails()
            instance.clientname=clientname
            instance.username=username
            instance.password=password
            instance.email=email
            instance.date=date
            instance.image=image
            instance.role=role
            instance.save()

            forlogin=logindetails()
            forlogin.role=role
            forlogin.username=username
            forlogin.password=password
            forlogin.save()

            messages.success(request, "Form submitted successfully")
            return render(request, 'SAdmin_ClientDetails.html')

#for taking campaign data SA
def taskcreation(request):
    cur, conn = sqlconn()
    print(request.method)

    if request.method == 'GET':
        q = 'SELECT id, clientname FROM market_clientdetails'
        cur.execute(q)
        people = list(cur.fetchall())
        return render(request, 'taskcreation.html', {'people': people})
    elif request.method=='POST':
        people=requirements.objects.all().values()
        campaign_name=request.POST['campaign_name']

        if requirements.objects.filter(campaign_name=campaign_name).exists():
            messages.error(request, "Campaign already registered!")
            return render(request, 'taskcreation.html', {'people':people})
        else:
            op=request.POST.getlist('option')
            sel_col=request.POST.getlist('selected_col')
            cl_access=request.POST.getlist('client_access')
            if request.POST.getlist('option') is None:
                op=[]
            if request.POST.getlist('selected_col') is None:
                sel_col=[]
            if request.POST.getlist('client_access') is None:
                cl_access=[]

            name=request.POST.get('name') #contains deptid and client
            name=ast.literal_eval(name)
            # print('checking', request.POST.get('planned_impressions'))
            requirements(
                name=name[1],
                campaign_name=request.POST.get('campaign_name'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                sel_options=op,
                selected_col=sel_col,
                client_access=cl_access,
                planned_impressions=request.POST.get('planned_impressions'),
                planned_cpm=request.POST.get('planned_cpm'),
                planned_clicks=request.POST.get('planned_clicks'),
                planned_cpc=request.POST.get('planned_cpc'),
                planned_session=request.POST.get('planned_session'),
                planned_cps=request.POST.get('planned_cps'),
                planned_budget_impressions=request.POST.get('pl_budget_impression'),
                planned_budget_clicks=request.POST.get('pl_budget_clicks'),
                planned_budget_sessions=request.POST.get('pl_budget_sessions'),
                ctr=request.POST.get('ctr'),
                deptid_id=name[0]
            ).save()
            messages.success(request, "Form Submitted Successfully!")
            q='select id, clientname from market_clientdetails'
            cur.execute(q)
            people=list(cur.fetchall())
            conn.commit()
            return render(request, 'taskcreation.html', {'people':people})

#for showing requirements of campaign
def taskdata(request):
    data=requirements.objects.all()
    return render(request, 'SAdmin_Taskdata.html', {'data':data})

#for taking each day report in report form
def u_report(request):
    cur, conn=sqlconn()
    q1='select distinct deptid_id, clientname from market_clientdetails inner join market_requirements on market_clientdetails.id=deptid_id;'
    cur.execute(q1)
    people=list(cur.fetchall())
    empcontext=requirements.objects.all()
    context={'people':people, 'empcontext':empcontext}
    
    if request.method=='GET':
        return render(request, 'user_report.html', context)
    elif request.method=='POST':
        clientname=request.POST.get('hiddenclient')
        campaign_name=request.POST.get('hiddencampaign')
        date=request.POST['date']
        if clientname=='' or campaign_name=='':
            messages.error(request, 'Select Client and Campaign')
            return render(request, 'user_report.html', context)
        else:
            clientname=clientname.replace("r\n", " ")
            clientname=clientname.strip()
            campaign_name=campaign_name.replace("r\n", " ")
            campaign_name=campaign_name.strip()
            if user_report.objects.filter(Q(clientname=clientname) & Q (campaign_name=campaign_name) & Q (date=date)).exists():
                messages.error(request, "Given date already registered!")
                return render(request, 'user_report.html', context)
            else:
                q="select id from market_requirements where name='{}' and campaign_name='{}'".format(clientname, campaign_name)
                cur.execute(q)
                data=list(cur.fetchone())

                user_report(
                    clientname=clientname,
                    campaign_name=campaign_name,
                    date=request.POST.get('date'),
                    no_of_impressions=request.POST.get('no_of_impressions'),
                    no_of_clicks=request.POST.get('no_of_clicks'),
                    no_of_sessions=request.POST.get('no_of_sessions'),
                    cpm=request.POST.get('cpm'),
                    cpc=request.POST.get('cpc'),
                    cps=request.POST.get('cps'),
                    total_cpm=request.POST.get('total_cpm'),
                    total_cpc=request.POST.get('cpc'),
                    total_cps=request.POST.get('cps'),
                    ctr=request.POST.get('ctr'),
                    clientid_id=int(data[0])
                ).save()
                conn.commit()
                q1='select distinct deptid_id, clientname from market_clientdetails inner join market_requirements on market_clientdetails.id=deptid_id;'
                cur.execute(q1)
                people=list(cur.fetchall())
                empcontext=requirements.objects.all()
                context={'people':people, 'empcontext':empcontext}
                messages.success(request, "Form submitted successfully! ")
                return render(request, 'user_report.html', context)


##REPORT DETAILS----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________
# import datetime
# def status(x):
#     #print('status:',x)
#     x = list(x)
#     date = str(datetime.date.today())
#     stdate = x[-2]
#     enddate = x[-1]
#     #print(stdate,enddate,type(stdate))
#     if date <=enddate and date >= stdate :
#         status = 'Running'
#     elif date > enddate and date >= stdate:
#         status = 'Closed'
#     else:
#         status = 'Pending'
#     x = x[:-2]
#     x.append(status)
#     return status

# def planning(p,d):
#     cur,conn = sqlconn()
#     print(p,d)
#     data = requirements.objects.filter(Q(deptid=p) & Q(campaign_name=d)).values('sel_options','planned_budget_impressions', 'planned_budget_clicks', 'planned_budget_sessions' )
#     data=list(data)[0]
#     newdata={}
#     achived={}
#     budget_col = []
#     print(data)
#     for j in ast.literal_eval(data['sel_options']):
#         if j == 'impressions':
#             newdata['planned_budget_impressions']=float(data['planned_budget_impressions'])
#             budget_col.append('total_cpm')
#             achived['total_cpm']=0
#         elif j=='clicks':
#             newdata['planned_budget_clicks']=float(data['planned_budget_clicks'])
#             budget_col.append('total_cpc')
#             achived['total_cpc']=0
#         else:
#             newdata['planned_budget_sessions']=float(data['planned_budget_sessions'])
#             budget_col.append('total_cps')
#             achived['total_cps']=0
    
#     #total_bud = user_report.objects.filter(Q(clientid_id=p) & Q(campaign_name=d)).values(x for x in budget_col)
#     q=f"select {', '.join(budget_col)}  from market_user_report inner join market_requirements on market_requirements.id = clientid_id where deptid_id={p} and market_user_report. campaign_name='{d}'"
#     cur.execute(q)
#     budget = cur.fetchall()
#     for i in budget:
#         for j in range(len(i)):
#                 #print('ach',achived[budget_col[j]])
#                 achived[budget_col[j]]=achived[budget_col[j]]+i[j]
#             #print(functools.reduce(lambda a, b: a[j]+b[j], i))

#     #print(budget)
#     print('achhived:',achived)

#     print(q)
#     return newdata,achived
#     #print(budget_col)
#     #print(newdata)

# from django.http import JsonResponse

# def fetch_dependent_options(request):
#     parent_value = request.GET.get('parentValue')
#     dependent_options = requirements.objects.filter(deptid=parent_value).values('campaign_name')
#     dependent_Options=list(dependent_options)
#     for i in dependent_Options:
#         #print(i['campaign_name'])
#         data=user_report.objects.filter(campaign_name=i['campaign_name']).values()
#         if len(data)==0:
#             dependent_Options.remove(i)
#         #print(len(data))
#     #print(dependent_Options)

#     return JsonResponse(dependent_Options, safe=False)





# ##report details

# def reportdata(request):
#     cur, conn=sqlconn()
#     q="select deptid_id, clientname from market_clientdetails inner join market_requirements on market_clientdetails.id=deptid_id;"
#     cur.execute(q)
#     people=list(cur.fetchall())
#     empcontext=requirements.objects.all()
#     if request.method=='POST':
#         datef=request.POST.get('datef')
#         datet=request.POST.get('datet')
#         parentValue=request.POST.get('parentValue')
#         dependValue=request.POST.get('dependValue')

#         head=['market_user_report.id', 'clientname', 'market.campaign_name', 'date', 'no_of_impressions', 'no_of_clicks', 'no_of_sessions', 'cpm', 'cpc', 'cps', 'total_cpm', 'total_cpc', 'total_cps', 'market_user_report.ctr', 'clientid_id']
#         print(parentValue, dependValue)
#         ##
#         date_Presence=False
#         if(datef is not None and datef !='') and (datet is not None and datet !=''):
#             date_Presence=True
#         camp_name=None

#         if parentValue is all and dependValue is None:
#             if date_Presence:
#                 q=f'select market_user_report.id, market_user_report.clientname, market_user_report.campaign_name, date, no_impressions, no_of_clicks, no_of_sessions, cpm, cpc, cps, total_cpm, total_cpc, total_cps, market_user_report.ctr, planned_budget_impressions, planned_budget_clicks, planned_budget_sessions, start_date, end_date from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and (date>= "{datef}" and date<="{datet}") order by date desc;'
#             else:
#                 q=f'select market_user_report.id, market_user_report.clientname, market_user_report.campaign_name, date, no_impressions, no_of_clicks, no_of_sessions, cpm, cpc, cps, total_cpm, total_cpc, total_cps, market_user_report.ctr, planned_budget_impressions, planned_budget_clicks, planned_budget_sessions, start_date, end_date from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name order by date desc;'
#         elif parentValue != all and (dependValue =='' or dependValue is None):
#             q1='select campaign_name, selected_col from market_requirements where deptid_id="{}" and campaign_name="{}"'.format(parentValue, dependValue)
#             cur.execute(q1)
#             res = cur.fetchone()
#             camp=res[0]
#             sel=ast.literal_eval(res[1])
#             camp_name=camp.upper()
#             col=head[:4]
#             for i in head:
#                 for i in sel:
#                     col.append(i)
#                 for j in sel:
#                     if j in i and j!=i:
#                         col.append(i)
#             if 'no_of_sessions' in col:
#                 col.insert(-1, 'total_cps')
#             if date_Presence:
#                 query=f'select {", ".join(col)}, planned_budget_impressions, planned_budget_clicks, planned_budget_sessions, start_date, end_date' + f'from market_user_report inner join market_requirements on clientid_id=market_requirements.id where market_user_report.campaign_name=market_requirements.campaign_name and market_requirements.deptid_id={parentValue} and market_requirements.campaign_name="{camp}" and (date >= "{datef}" and date<= "{datet}") order by date desc;'
#             else:
#                 query=f'select {", ".join(col)}, planned_budget_impressions, planned_budget_clicks, planned_budget_sessions, start_date, end_date' + f'from market_user_report inner join market_requirements on clientid_id=market_requirements.id where market_user_report.campaign_name=market_requirements.campaign_name and market_requirements.deptid_id={parentValue} and market_requirements.campaign_name="{camp}" order by date desc;'
            
#             cur.execute(query)
#             headers = [i[0] for i in cur.description]
#             data=list(cur.fetchall())
#             report=list(map(lambda x:list(x[1:-5]), data))
#             f_data=list(map(lambda x:{'id':x[0], 'values':list(x[1:-5])}, data))
#             tr=[]
#             pl = 'NOT SET' if data[0][-1]=='' else float(data[0][-1])
#             ach =functools.reduce(lambda a,b:a+b,list(map(lambda l:l[-4],data)))
#             for i in range(len(pl)):
#                 x=list(pl.keys())
#                 y=list(ach.keys())
#                 if float(pl[x[i]])<float(ach[y[i]]) and float(pl[x[i]])!=0:
#                     tr.append('Hit')
#                 elif float(pl[x[i]])==0:
#                     tr.append("Not set")
#                 else:
#                     tr.append("Not hit")
#             conn.commit()
#             return render(request, 'SAdmin_Reportdata.html', {'data':json.dumps(f_data),'col':json.dumps(headers[1:-5]),'rd':json.dumps(report),'planned':pl,'achived':achv,'target':tr,'people':people,'empcontext':empcontext,'status':status(data[0]),'camp_name':camp_name,})
#         else:
#             q1='select selected_col from market_requirements where deptid_id = "{}" and campaign_name = "{}" '.format(parentValue,dependValue)
#             cur.execute(q1)
#             head=['market_user_report.id', 'clientname', 'market.campaign_name', 'date', 'no_of_impressions', 'no_of_clicks', 'no_of_sessions', 'cpm', 'cpc', 'cps', 'total_cpm', 'total_cpc', 'total_cps', 'market_user_report.ctr', 'clientid_id']
#             sel=ast.literal_eval(cur.fetchone()[0])
#             col=head[:4]
#             for i in head:
#                 if i in sel:
#                     col.append(i)
#                 for j in sel:
#                     if j in i and j!=i:
#                         col.append(i)
#             if 'no_of_sessions' in col:
#                 col.insert(-1,'total_cps')

#             pl,achv=planning(parentValue,dependValue)
#             print(pl,achv)
#             #print('col',col)
#             if date_Presence:
#                 query = f"select {', '.join(col)},planned_budget_impressions, planned_budget_clicks, planned_budget_sessions ,start_date,end_date"+f" from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and market_requirements.deptid_id ={parentValue} and market_requirements.campaign_name='{dependValue}' and (date >= '{datef}' and date <='{datet}') order by date desc;"
#             else:
            
#                 query = f"select {', '.join(col)},planned_budget_impressions, planned_budget_clicks, planned_budget_sessions ,start_date,end_date"+f" from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and market_requirements.deptid_id ={parentValue} and market_requirements.campaign_name='{dependValue}' order by date desc;"
            
#             camp_name = dependValue.upper()
#             cur.execute(query)
#             headers = [i[0] for i in cur.description]
#             #print('col',headers)
#             data = list(cur.fetchall())
#             #print(data)    
#             #ach =functools.reduce(lambda a,b:a+b,list(map(lambda l:l[-4],data)))
#             #pl = 'NOT SET' if data[0][-1]=='' else float(data[0][-1])
#             report = list(map(lambda x:list(x[1:-5]),data))
#             f_data = list(map(lambda x:{'id':x[0],'values':list(x[1:-5])},data))
#             tr=[]
#             for i in range(len(pl)):
#                x= list(pl.keys())
#                y=list(achv.keys())
#                if float(pl[x[i]]) < float(achv[y[i]]) and float(pl[x[i]])!=0:
#                    tr.append('Hit')
#                elif float(pl[x[i]]) ==0:
#                    tr.append('Not Set')
#                else:
#                     tr.append('Not Hit')
                
#                print(x,y)
#                 #print('data',f_data)
#             conn.commit()
#             return render(request,'SAdmin_Reportdata.html',{'data':json.dumps(f_data),'col':json.dumps(headers[1:-5]),'rd':json.dumps(report),'planned':pl,'achived':achv,'target':tr,'people':people,'empcontext':empcontext,'status':status(data[0]),'camp_name':camp_name,})     
#         #q='select * from market_user_report'
#         cur.execute(q)
#         headers = [i[0] for i in cur.description]
#         #print(headers)
#         data = list(cur.fetchall())
#         conn.commit()
#         report = list(map(lambda x:list(x[1:-5]),data))
#         data = list(map(lambda x:{'id':x[0],'values':list(x[1:-5])},data))
#         #print('RData',data)
#         #rd = list(map(status,data))
        
#         #print(data[0],status(data[0]))
#         #ach =functools.reduce(lambda a,b:a+b,list(map(lambda l:l[-4],data)))
        
#         #print(functools.reduce(lambda a,b:a+b,list(map(lambda l:l[-4],rd))))
#         #rd=user_report.objects.all()
#         #print(queryset)
#         #return render(request,'searchresult.html',{'queryset':queryset})
#         #return render(request,'SAdmin_Reportdata.html',{'rd':rd})
#         #return render(request,'sky.html',{'people':people,'empcontext':empcontext})
#         return render(request,'SAdmin_Reportdata.html',{'data':json.dumps(data),'col':json.dumps(headers[1:-5]),'rd':json.dumps(report),'people':people,'empcontext':empcontext,'camp_name':None})
#     else:
#         #print('sky')
#         q = 'select market_user_report.id,market_user_report.clientname, market_user_report.campaign_name,date, no_of_impressions,no_of_clicks,no_of_sessions,cpm,cpc,cps,total_cpm,total_cpc,total_cps,market_user_report.ctr,start_date,end_date from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name order by date desc;'
#         cur.execute(q)
#         headers = [i[0] for i in cur.description]
#         #print(headers)
#         data = list(cur.fetchall())
#         conn.commit()
#         #print('in_data',data)
#         report = list(map(lambda x:list(x[1:-2]),data))
#         data = list(map(lambda x:{'id':x[0],'values':list(x[1:-2])},data))
#         #print('RData',data)
#         #print('planned',data)
#         #rd = data
#         return render(request,'SAdmin_Reportdata.html',{'data':json.dumps(data),'col':json.dumps(headers[1:-2]),'rd':json.dumps(report),'people':people,'empcontext':empcontext,'camp_name':None})

            
# ##REPORT DETAILS----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________
###Original
#*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||
import datetime
def status(x):
    #print('status:',x)
    x = list(x)
    date = str(datetime.date.today())
    stdate = x[-2]
    enddate = x[-1]
    #print(stdate,enddate,type(stdate))
    if date <=enddate and date >= stdate :
        status = 'Running'
    elif date > enddate and date >= stdate:
        status = 'Closed'
    else:
        status = 'Pending'
    x = x[:-2]
    x.append(status)
    return status

def planning(p,d):
    cur,conn = sqlconn()
    print(p,d)
    data = requirements.objects.filter(Q(deptid=p) & Q(campaign_name=d)).values('sel_options','planned_budget_impressions', 'planned_budget_clicks', 'planned_budget_sessions' )
    data=list(data)[0]
    newdata={}
    achived={}
    budget_col = []
    print(data)
    for j in ast.literal_eval(data['sel_options']):
        if j == 'impressions':
            newdata['planned_budget_impressions']=float(data['planned_budget_impressions'])
            budget_col.append('total_cpm')
            achived['total_cpm']=0
        elif j=='clicks':
            newdata['planned_budget_clicks']=float(data['planned_budget_clicks'])
            budget_col.append('total_cpc')
            achived['total_cpc']=0
        else:
            newdata['planned_budget_sessions']=float(data['planned_budget_sessions'])
            budget_col.append('total_cps')
            achived['total_cps']=0
    
    #total_bud = user_report.objects.filter(Q(clientid_id=p) & Q(campaign_name=d)).values(x for x in budget_col)
    q=f"select {', '.join(budget_col)}  from market_user_report inner join market_requirements on market_requirements.id = clientid_id where deptid_id={p} and market_user_report. campaign_name='{d}'"
    cur.execute(q)
    budget = cur.fetchall()
    for i in budget:
        for j in range(len(i)):
                #print('ach',achived[budget_col[j]])
                achived[budget_col[j]]=achived[budget_col[j]]+i[j]
            #print(functools.reduce(lambda a, b: a[j]+b[j], i))

    #print(budget)
    print('achhived:',achived)

    print(q)
    return newdata,achived
    #print(budget_col)
    #print(newdata)

#------------------------------------------report details page --------------------------------
from django.http import JsonResponse

def fetch_dependent_options(request):
    parent_value = request.GET.get('parentValue')
    dependent_options = requirements.objects.filter(deptid=parent_value).values('campaign_name')
    dependent_Options=list(dependent_options)
    for i in dependent_Options:
        #print(i['campaign_name'])
        data=user_report.objects.filter(campaign_name=i['campaign_name']).values()
        if len(data)==0:
            dependent_Options.remove(i)
        #print(len(data))
    #print(dependent_Options)

    return JsonResponse(dependent_Options, safe=False)
'''
def fetch_data(request):
    print(request.GET.get('parentValue'))
    parentValue = request.GET.get('parentValue')
    dependValue = request.GET.get('dependValue')
    print(request.GET.get('dependValue'))
    cur,conn = sqlconn()
    q=''
    if parentValue == 'all' and dependValue is None:
        q = 'select market_user_report.id,market_user_report.clientname,  market_user_report.campaign_name,date, no_of_impressions,no_of_clicks,no_of_sessions,cpm,cpc,cps,total_cpm,total_cpc,total_cps,total_cost,ctr,start_date,end_date from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name order by date desc;'
    elif parentValue != 'all' and dependValue=='':
        q1="select campaign_name from market_requirements where deptid_id = {}".format(parentValue)
        cur.execute(q1)
        res = cur.fetchone()[0]
        #print(res)
        q = "select market_user_report.id,market_user_report.clientname,  market_user_report.campaign_name,date, no_of_impressions,no_of_clicks,no_of_sessions,cpm,cpc,cps,total_cpm,total_cpc,total_cps,ctr,start_date,end_date from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and market_requirements.deptid_id ={} and market_requirements.campaign_name='{}' order by date desc;".format(parentValue,res)
    else:
        q = "select market_user_report.id,market_user_report.clientname,  market_user_report.campaign_name,date, no_of_impressions,no_of_clicks,no_of_sessions,cpm,cpc,cps,total_cpm,total_cpc,total_cps,ctr,start_date,end_date from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and market_requirements.deptid_id ={} and market_requirements.campaign_name='{}' order by date desc;".format(parentValue,dependValue)
        
    cur.execute(q)
    data = list(cur.fetchall())
    conn.commit()
    rd = list(map(status,data))
    #print(rd)
    return  JsonResponse(rd, safe=False)
'''

import functools
import json

def reportdata(request):
    #print(request)
    cur,conn = sqlconn()
    q1 = 'select DISTINCT deptid_id ,clientname from market_clientdetails inner join market_requirements on market_clientdetails.id =  deptid_id;'
    cur.execute(q1)
    people = list(cur.fetchall()) 
    empcontext = requirements.objects.all()    
    #context={'people':people,'empcontext':empcontext}
    if request.method=="POST":
        #print(request)
        datef=request.POST.get("datef")
        datet=request.POST.get("datet")
        parentValue = request.POST.get('parentValue')
        dependValue = request.POST.get('dependValue')

        head = ['market_user_report.id', 'clientname', 'market_user_report.campaign_name', 'date', 'no_of_impressions', 'no_of_clicks', 'no_of_sessions', 'cpm', 'cpc', 'cps', 'total_cpm', 'total_cpc', 'total_cps', 'market_user_report.ctr', 'clientid_id']
        print(parentValue,dependValue)
        #print(datef,datet) 
        query = ''
        date_Presence=False
        if (datef is not None and datef != '') and (datet is not None and datet != ''):
            date_Presence = True

        camp_name = None
        if parentValue == 'all' and dependValue is None:
            if date_Presence:
                q = f'select market_user_report.id,market_user_report.clientname,  market_user_report.campaign_name,date, no_of_impressions,no_of_clicks,no_of_sessions,cpm,cpc,cps,total_cpm,total_cpc,total_cps,market_user_report.ctr,planned_budget_impressions, planned_budget_clicks, planned_budget_sessions ,start_date,end_date from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and (date >= "{datef}" and date <="{datet}") order by date desc;'
                #print('hey')
            else:
                q = 'select market_user_report.id,market_user_report.clientname,  market_user_report.campaign_name,date, no_of_impressions,no_of_clicks,no_of_sessions,cpm,cpc,cps,total_cpm,total_cpc,total_cps,market_user_report.ctr,planned_budget_impressions, planned_budget_clicks, planned_budget_sessions ,start_date,end_date from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name order by date desc;'
        elif parentValue != 'all' and (dependValue=='' or dependValue is None):
                #print('comening')
            q1="select campaign_name,selected_col from market_requirements where deptid_id = {}".format(parentValue)
            cur.execute(q1)
            res = cur.fetchone()
            camp=res[0]
            sel=ast.literal_eval(res[1])
                #print(sel)
            camp_name = camp.upper()
                #col=[]
            print(camp,parentValue)
            col=head[:4]
            for i in head:
                if i in sel:
                    col.append(i)
                for j in sel:
                    if j in i and j!=i:
                        col.append(i)
            if 'no_of_sessions' in col:
                col.insert(-1,'total_cps')
            if date_Presence:
                query = f"select {', '.join(col)} ,planned_budget_impressions, planned_budget_clicks, planned_budget_sessions ,start_date,end_date"+f" from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and market_requirements.deptid_id ={parentValue} and market_requirements.campaign_name='{camp}' and (date >= '{datef}' and date <='{datet}') order by date desc;"
            else:
                query = f"select {', '.join(col)} ,planned_budget_impressions, planned_budget_clicks, planned_budget_sessions  ,start_date,end_date"+f" from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and market_requirements.deptid_id ={parentValue} and market_requirements.campaign_name='{camp}' order by date desc;"

            cur.execute(query)
            headers = [i[0] for i in cur.description]
            #print('col',headers)
            data = list(cur.fetchall())
            #ach =functools.reduce(lambda a,b:a+b,list(map(lambda l:l[-4],data)))
            #pl = 'NOT SET' if data[0][-1]=='' else float(data[0][-1])
            report = list(map(lambda x:list(x[1:-5]),data))
            f_data = list(map(lambda x:{'id':x[0],'values':list(x[1:-5])},data))
            tr=[]
            for i in range(len(pl)):
               x= list(pl.keys())
               y=list(achv.keys())
               if float(pl[x[i]]) < float(achv[y[i]]) and float(pl[x[i]])!=0:
                   tr.append('Hit')
               elif float(pl[x[i]]) ==0:
                   tr.append('Not Set')
               else:
                    tr.append('Not Hit')
                
               print(x,y)
                #print('data',f_data)
            conn.commit()
            return render(request,'SAdmin_Reportdata.html',{'data':json.dumps(f_data),'col':json.dumps(headers[1:-5]),'rd':json.dumps(report),'planned':pl,'achived':achv,'target':tr,'people':people,'empcontext':empcontext,'status':status(data[0]),'camp_name':camp_name,})
                
        else:
            q1="select selected_col from market_requirements where deptid_id = {} and campaign_name = '{}' ".format(parentValue,dependValue)
            cur.execute(q1)
                #col=[]
            head = ['market_user_report.id', 'clientname', 'market_user_report.campaign_name', 'date', 'no_of_impressions', 'no_of_clicks', 'no_of_sessions', 'cpm', 'cpc', 'cps', 'total_cpm', 'total_cpc', 'total_cps', 'market_user_report.ctr', 'clientid_id']
            sel = ast.literal_eval(cur.fetchone()[0])
            #print('selcol',sel)
            col=head[:4]
            for i in head:
                if i in sel:
                    col.append(i)
                for j in sel:
                    if j in i and j!=i:
                        col.append(i)
            if 'no_of_sessions' in col:
                col.insert(-1,'total_cps')

            pl,achv=planning(parentValue,dependValue)
            print(pl,achv)
            #print('col',col)
            if date_Presence:
                query = f"select {', '.join(col)},planned_budget_impressions, planned_budget_clicks, planned_budget_sessions ,start_date,end_date"+f" from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and market_requirements.deptid_id ={parentValue} and market_requirements.campaign_name='{dependValue}' and (date >= '{datef}' and date <='{datet}') order by date desc;"
            else:
            
                query = f"select {', '.join(col)},planned_budget_impressions, planned_budget_clicks, planned_budget_sessions ,start_date,end_date"+f" from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and market_requirements.deptid_id ={parentValue} and market_requirements.campaign_name='{dependValue}' order by date desc;"
                #print('col',query)
                
                #q = "select market_user_report.id,market_user_report.clientname, market_user_report.campaign_name,date, no_of_impressions,no_of_clicks,no_of_sessions,cpm,cpc,cps,total_cpm,total_cpc,total_cps,total_cost,market_user_report.ctr,start_date,end_date,planned_cost from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name and market_requirements.deptid_id ={} and market_requirements.campaign_name='{}' order by date desc;".format(parentValue,dependValue)
            camp_name = dependValue.upper()
            #print('q:',query)
            cur.execute(query)
            headers = [i[0] for i in cur.description]
            #print('col',headers)
            data = list(cur.fetchall())
            #print(data)    
            #ach =functools.reduce(lambda a,b:a+b,list(map(lambda l:l[-4],data)))
            #pl = 'NOT SET' if data[0][-1]=='' else float(data[0][-1])
            report = list(map(lambda x:list(x[1:-5]),data))
            f_data = list(map(lambda x:{'id':x[0],'values':list(x[1:-5])},data))
            tr=[]
            for i in range(len(pl)):
               x= list(pl.keys())
               y=list(achv.keys())
               if float(pl[x[i]]) < float(achv[y[i]]) and float(pl[x[i]])!=0:
                   tr.append('Hit')
               elif float(pl[x[i]]) ==0:
                   tr.append('Not Set')
               else:
                    tr.append('Not Hit')
                
               print(x,y)
                #print('data',f_data)
            conn.commit()
            return render(request,'SAdmin_Reportdata.html',{'data':json.dumps(f_data),'col':json.dumps(headers[1:-5]),'rd':json.dumps(report),'planned':pl,'achived':achv,'target':tr,'people':people,'empcontext':empcontext,'status':status(data[0]),'camp_name':camp_name,})     
        #q='select * from market_user_report'
        cur.execute(q)
        headers = [i[0] for i in cur.description]
        #print(headers)
        data = list(cur.fetchall())
        conn.commit()
        report = list(map(lambda x:list(x[1:-5]),data))
        data = list(map(lambda x:{'id':x[0],'values':list(x[1:-5])},data))
        #print('RData',data)
        #rd = list(map(status,data))
        
        #print(data[0],status(data[0]))
        #ach =functools.reduce(lambda a,b:a+b,list(map(lambda l:l[-4],data)))
        
        #print(functools.reduce(lambda a,b:a+b,list(map(lambda l:l[-4],rd))))
        #rd=user_report.objects.all()
        #print(queryset)
        #return render(request,'searchresult.html',{'queryset':queryset})
        #return render(request,'SAdmin_Reportdata.html',{'rd':rd})
        #return render(request,'sky.html',{'people':people,'empcontext':empcontext})
        return render(request,'SAdmin_Reportdata.html',{'data':json.dumps(data),'col':json.dumps(headers[1:-5]),'rd':json.dumps(report),'people':people,'empcontext':empcontext,'camp_name':None})
    else:
        #print('sky')
        q = 'select market_user_report.id,market_user_report.clientname, market_user_report.campaign_name,date, no_of_impressions,no_of_clicks,no_of_sessions,cpm,cpc,cps,total_cpm,total_cpc,total_cps,market_user_report.ctr,start_date,end_date from market_user_report inner join market_requirements on clientid_id = market_requirements.id where market_user_report.campaign_name = market_requirements.campaign_name order by date desc;'
        cur.execute(q)
        headers = [i[0] for i in cur.description]
        #print(headers)
        data = list(cur.fetchall())
        conn.commit()
        #print('in_data',data)
        report = list(map(lambda x:list(x[1:-2]),data))
        data = list(map(lambda x:{'id':x[0],'values':list(x[1:-2])},data))
        #print('RData',data)
        #print('planned',data)
        #rd = data
        return render(request,'SAdmin_Reportdata.html',{'data':json.dumps(data),'col':json.dumps(headers[1:-2]),'rd':json.dumps(report),'people':people,'empcontext':empcontext,'camp_name':None})
        #return render(request,'sky.html',{'rd':rd,'people':people,'empcontext':str(list(empcontext.values()))})

# ##REPORT DETAILS----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________----------__________
#*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||*****_____-----|||||



##USER TASK CREATION

def taskcreation_user(request):
    cur, conn=sqlconn()
    q='select id, clientname from market_clientdetails'
    cur.execute(q)
    people=list(cur.fetchall())
    if request.method=='GET':
        return render(request, 'taskcreation_user.html', {'people':people})
    elif request.method=='POST':
        campaign_name=request.POST.get('campaign_name')
        if requirements.objects.filter(campaign_name=campaign_name).exists():
            messages.error(request, "Campaign Already Registered!")
            return render(request, 'taskcreation_user.html', {'people':people})
        else:
            op=request.POST.getlist('option')
            sel_col=request.POST.getlist('selected_col')
            cl_access=request.POST.getlist('client_access')
            if request.POST.getlist('option') is None:
                op=[]
            if request.POST.getlist('selected_col') is None:
                sel_col=[]
            if request.POST.getlist('client_access') is None:
                cl_access=[]
            
            name=request.POST.get('name')  #it has id and client name
            name=ast.literal_eval(name)

        requirements(
                name=name[1],
                campaign_name=request.POST.get('campaign_name'),
                start_date=request.POST.get('start_date'),
                end_date=request.POST.get('end_date'),
                sel_options=op,
                selected_col=sel_col,
                client_access=cl_access,
                planned_impressions=request.POST.get('planned_impressions'),
                planned_cpm=request.POST.get('planned_cpm'),
                planned_clicks=request.POST.get('planned_clicks'),
                planned_cpc=request.POST.get('planned_cpc'),
                planned_session=request.POST.get('planned_session'),
                planned_cps=request.POST.get('planned_cps'),
                planned_budget_impressions = request.POST.get('pl_budget_impression'),
                planned_budget_clicks =  request.POST.get('pl_budget_clicks'),
                planned_budget_sessions = request.POST.get('pl_budget_sessions'),
                ctr=request.POST.get('ctr'),
                deptid_id=name[0]
            ).save()
        messages.success(request, "Form successfully submitted!")
        return render(request, 'taskcreation_user.html', {'people':people})
    

##USER REPORT FORM

# def report_user(request):
#     cur, conn=sqlconn()
#     q="select name, "

def report_user(request):
    cur,conn= sqlconn()
    if request.method=='GET':
        #people = clientdetails.objects.all()
        #deptcontext = clientdetails.objects.all()
        q1 = 'select DISTINCT deptid_id ,clientname from market_clientdetails inner join market_requirements on market_clientdetails.id =  deptid_id;'
        cur.execute(q1)
        people = list(cur.fetchall()) 
        empcontext = requirements.objects.all()    
        context={'people':people,'empcontext':empcontext}
        #print(people ,'\n', empcontext)
        return render(request,'user_report_user.html',context)

