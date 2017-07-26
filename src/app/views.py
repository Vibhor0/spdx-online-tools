# -*- coding: utf-8 -*-

# Copyright (c) 2017 Rohit Lodha
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import unicode_literals

from django.shortcuts import render,render_to_response
from django.http import HttpResponse,HttpResponseRedirect,HttpResponseBadRequest,JsonResponse,HttpResponseForbidden
from django.contrib.auth import authenticate,login ,logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django import forms
from django.template import RequestContext
from django.core.files.storage import FileSystemStorage

from app.models import UserID
from app.forms import UserRegisterForm,UserProfileForm

import jpype
import traceback
import os
import json


def index(request):
    context_dict={}
    return render(request, 'app/index.html',context_dict)

def about(request):
    context_dict={}
    return render(request, 'app/about.html',context_dict)

def validate(request):
    context_dict={}
    if request.method == 'POST':
        if (jpype.isJVMStarted()==0):
            """ If JVM not already started, start it, attach a Thread and start processing the request """
            classpath =os.path.abspath(".")+"/tool.jar"
            jpype.startJVM(jpype.getDefaultJVMPath(),"-ea","-Djava.class.path=%s"%classpath)
        """ If JVM started, attach a Thread and start processing the request """
        jpype.attachThreadToJVM()
        package = jpype.JPackage("org.spdx.tools")
        verifyclass = package.Verify
        try :
            if request.FILES["file"]:
                """ Saving file to the media directory """
                myfile = request.FILES['file']
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
                """ Call the java function with parameters as list"""
                verifyclass.verify(settings.APP_DIR+uploaded_file_url)
                verifyclass.main([settings.APP_DIR+uploaded_file_url])
                if (request.is_ajax()):
                    ajaxdict=dict()
                    ajaxdict["data"] = "This SPDX Document is valid."
                    response = json.dumps(ajaxdict)
                    jpype.detachThreadFromJVM()
                    return HttpResponse(response)
                jpype.detachThreadFromJVM()
                return HttpResponse("This SPDX Document is valid.")
            else :
                jpype.detachThreadFromJVM()
                return HttpResponse("File Not Uploaded")
        except jpype.JavaException,ex :
            """ Error raised by verifyclass.verify without exiting the application"""
            context_dict["error"] = jpype.JavaException.message(ex) #+ "This SPDX Document is not a valid RDF/XML or tag/value format"
            if (request.is_ajax()):
                ajaxdict=dict()
                ajaxdict["data"] = jpype.JavaException.message(ex)
                response = json.dumps(ajaxdict)
                jpype.detachThreadFromJVM()
                return HttpResponse(response,status=400)
            jpype.detachThreadFromJVM()
            return render(request, 'app/validate.html',context_dict)
        except :
            traceback.print_exc()
            context_dict["error"] = "Other Exception Raised." 
            if (request.is_ajax()):
                ajaxdict=dict()
                ajaxdict["data"] = "Other Exception Raised." 
                response = json.dumps(ajaxdict)
                jpype.detachThreadFromJVM()
                return HttpResponse("Other Exception Raised.",status=400)
            jpype.detachThreadFromJVM()    
            return render(request, 'app/validate.html',context_dict)
    else :
        return render(request, 'app/validate.html',context_dict)

def compare(request):
    context_dict={}
    if request.method == 'POST':
        if (jpype.isJVMStarted()==0):
            """ If JVM not already started, start it, attach a Thread and start processing the request """
            classpath =os.path.abspath(".")+"/tool.jar"
            jpype.startJVM(jpype.getDefaultJVMPath(),"-ea","-Djava.class.path=%s"%classpath)
        """ If JVM started, attach a Thread and start processing the request """
        jpype.attachThreadToJVM()
        package = jpype.JPackage("org.spdx.tools")
        verifyclass = package.Verify
        mainclass = package.Main
        if 'compare' in request.POST:
            try :
                if request.FILES["file1"]:
                    nofile = int(request.POST["nofile"])
                    rfilename = request.POST["rfilename"]+".xlsx"
                    callfunc = ["CompareMultipleSpdxDocs",settings.MEDIA_ROOT+"/"+rfilename]
                    for i in range(1,nofile+1):
                        """ Saving file to the media directory """
                        try:
                            a = 'file'+str(i)
                            myfile = request.FILES['file'+str(i)]
                        except:
                            traceback.print_exc()
                            return HttpResponse("File does not exist")
                        fs = FileSystemStorage()
                        filename = fs.save(myfile.name, myfile)
                        uploaded_file_url = fs.url(filename)
                        verifyclass.verify(settings.APP_DIR+uploaded_file_url)
                        callfunc.append(settings.APP_DIR+uploaded_file_url)
                    """ Call the java function with parameters as list"""
                    mainclass.main(callfunc)
                    context_dict['Content-Disposition'] = 'attachment; filename='+filename
                    if (request.is_ajax()):
                        ajaxdict=dict()
                        ajaxdict["medialink"] = "/media/" + rfilename
                        response = json.dumps(ajaxdict)
                        jpype.detachThreadFromJVM()
                        return HttpResponse(response)
                    jpype.detachThreadFromJVM()
                    return HttpResponseRedirect("/media/"+rfilename)
                else :
                    jpype.detachThreadFromJVM()
                    return HttpResponse("File Not Uploaded",status=404)
            except jpype.JavaException,ex :
                """ Error raised by verifyclass.verify without exiting the application"""
                context_dict["error"] = jpype.JavaException.message(ex) #+ "This SPDX Document is not a valid RDF/XML or tag/value format"
                if (request.is_ajax()):
                    ajaxdict=dict()
                    ajaxdict["data"] = jpype.JavaException.message(ex)
                    response = json.dumps(ajaxdict)
                    jpype.detachThreadFromJVM()
                    return HttpResponse(response,status=400)
                jpype.detachThreadFromJVM()
                return render(request, 'app/compare.html',context_dict)
            except :
                traceback.print_exc()
                context_dict["error"] = "Other Exception Raised." 
                if (request.is_ajax()):
                    ajaxdict=dict()
                    ajaxdict["data"] = "Other"
                    response = json.dumps(ajaxdict)
                    jpype.detachThreadFromJVM()
                    return HttpResponse(response,status=400)
                jpype.detachThreadFromJVM()    
                return render(request, 'app/compare.html',context_dict)
        elif 'compareall' in request.POST:
            try :
                if request.FILES["files"]:
                    rfilename = request.POST["rfilename"]+".xlsx"
                    callfunc = ["CompareMultipleSpdxDocs",settings.MEDIA_ROOT+"/"+rfilename]
                    # loop through the list of files
                    for myfile in request.FILES.getlist("files"):
                        fs = FileSystemStorage()
                        filename = fs.save(myfile.name, myfile)
                        uploaded_file_url = fs.url(filename)
                        verifyclass.verify(settings.APP_DIR+uploaded_file_url)
                        callfunc.append(settings.APP_DIR+uploaded_file_url)
                    """ Call the java function with parameters as list"""
                    mainclass.main(callfunc)
                    context_dict['Content-Disposition'] = 'attachment; filename='+filename
                    if (request.is_ajax()):
                        ajaxdict=dict()
                        ajaxdict["medialink"] = "/media/" + rfilename
                        response = json.dumps(ajaxdict)
                        jpype.detachThreadFromJVM()
                        return HttpResponse(response)
                    jpype.detachThreadFromJVM()    
                    return HttpResponseRedirect("/media/"+rfilename)
                else :
                    jpype.detachThreadFromJVM()
                    return HttpResponse("File Not Uploaded",status=404)
            except jpype.JavaException,ex :
                """ Error raised by verifyclass.verify without exiting the application"""
                context_dict["error"] = jpype.JavaException.message(ex) #+ "This SPDX Document is not a valid RDF/XML or tag/value format"
                if (request.is_ajax()):
                    ajaxdict=dict()
                    ajaxdict["data"] = jpype.JavaException.message(ex)
                    response = json.dumps(ajaxdict)
                    jpype.detachThreadFromJVM()
                    return HttpResponse(response,status=400)
                jpype.detachThreadFromJVM()    
                return render(request, 'app/compare.html',context_dict)
            except :
                traceback.print_exc()
                context_dict["error"] = "Other Exception Raised." 
                if (request.is_ajax()):
                    ajaxdict=dict()
                    ajaxdict["data"] = "Other Exception"
                    response = json.dumps(ajaxdict)
                    jpype.detachThreadFromJVM()
                    return HttpResponse(response,status=400)
                jpype.detachThreadFromJVM()
                return render(request, 'app/compare.html',context_dict)
    else :
        return render(request, 'app/compare.html',context_dict)

def convert(request):
    context_dict={}
    if request.method == 'POST':
        if (jpype.isJVMStarted()==0):
            """ If JVM not already started, start it, attach a Thread and start processing the request """
            classpath =os.path.abspath(".")+"/tool.jar"
            jpype.startJVM(jpype.getDefaultJVMPath(),"-ea","-Djava.class.path=%s"%classpath)
        """ If JVM started, attach a Thread and start processing the request """
        jpype.attachThreadToJVM()
        package = jpype.JPackage("org.spdx.tools")
        mainclass = package.Main
        try :
            if request.FILES["file"]:
                """ Saving file to the media directory """
                myfile = request.FILES['file']
                fs = FileSystemStorage()
                filename = fs.save(myfile.name, myfile)
                uploaded_file_url = fs.url(filename)
                convertfile =  request.POST["cfilename"]+request.POST["cfileformat"]
                option1 = request.POST["from_format"]
                option2 = request.POST["to_format"]
                functiontocall = option1 + "To" + option2
                if (option1=="Tag" or option1=="RDF"):
                    print ("Verifing for Tag/Value or RDF Document")
                    verifyclass = package.Verify
                    verifyclass.verify(settings.APP_DIR+uploaded_file_url)
                """ Call the java function with parameters as list"""
                mainclass.main([functiontocall,settings.APP_DIR+uploaded_file_url,settings.MEDIA_ROOT+"/"+convertfile])
                jpype.detachThreadFromJVM()
                context_dict['Content-Disposition'] = 'attachment; filename='+filename
                if (request.is_ajax()):
                        ajaxdict=dict()
                        ajaxdict["data"] = "This SPDX Document is valid."
                        ajaxdict["medialink"] = "/media/" + convertfile
                        response = json.dumps(ajaxdict)
                        return HttpResponse(response)
                return HttpResponseRedirect("/media/" + convertfile)
            else :
                return HttpResponse("File Not Uploaded")
        except jpype.JavaException,ex :
            context_dict["error"] = jpype.JavaException.message(ex)
            jpype.detachThreadFromJVM()
            if (request.is_ajax()):
                ajaxdict=dict()
                ajaxdict["data"] = jpype.JavaException.message(ex)
                response = json.dumps(ajaxdict)
                return HttpResponse(response)
            return render(request, 'app/convert.html',context_dict)
        except :
            traceback.print_exc()
            context_dict["error"] = "Other Exception Raised."
            jpype.detachThreadFromJVM()
            if (request.is_ajax()):
                ajaxdict=dict()
                ajaxdict["data"] = "Other Exception Raised."
                response = json.dumps(ajaxdict)
                return HttpResponse(response)
            return render(request, 'app/convert.html',context_dict)
    else :
        return render(request, 'app/convert.html',context_dict)
def search(request):
    context_dict={}
    return render(request, 'app/search.html',context_dict)

def loginuser(request):
    context_dict={}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user and user.is_staff and not user.is_superuser:
            #add status  choice here
            if user.is_active:
                login(request, user)
                if (request.is_ajax()):
                    ajaxdict=dict()
                    ajaxdict["data"] = "Success"
                    ajaxdict["next"] = "/app/"
                    response = json.dumps(ajaxdict)
                    return HttpResponse(response)
                return HttpResponseRedirect('/app/')
            else:
                if (request.is_ajax()):
                    return HttpResponseForbidden("Your account is disabled.")
                return HttpResponse("Your account is disabled.")	
        else:
            if (request.is_ajax()):
                return HttpResponseForbidden("Invalid login details supplied.")
            context_dict['invalid']="Invalid login details supplied."
            print "Invalid login details: {0}, {1}".format(username, password)
            return render(request, 'app/login.html',context_dict)
    else:
        return render(request, 'app/login.html',context_dict)

def register(request):
    context_dict={}
    if request.method == 'POST':
        user_form = UserRegisterForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.is_staff=True
            profile = profile_form.save(commit=False)
            user.save()
            profile.user = user
            profile.save()
            registered = True
            return HttpResponseRedirect('/app/login/')
        else:
            print user_form.errors
            print profile_form.errors
    else:
        user_form = UserRegisterForm()
        profile_form = UserProfileForm()
        context_dict["user_form"]=user_form
        context_dict["profile_form"]=profile_form
    return render(request,'app/register.html',context_dict)

def logoutuser(request):
    logout(request)
    return HttpResponseRedirect("/app/")
