from django.shortcuts import render, redirect
from .forms import ResumeForm
from .models import Resume
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
import os
import requests
from dotenv import load_dotenv

load_dotenv()

# AI Feedback Function
def get_ai_feedback(resume_text):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{
                "text": f"Analyze this resume and provide professional feedback. Include evaluation of skills, experience, formatting, and areas for improvement:\n\n{resume_text}"
            }]
        }]
    }
    response = requests.post(f"{url}?key={os.getenv('GEMINI_API_KEY')}", json=data, headers=headers)
    try:
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except:
        return "⚠️ Unable to generate AI feedback at this time."

# Upload View
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            # Clear old session data
            request.session.pop('resume_id', None)
            request.session.pop('feedback', None)

            resume = form.save()
            request.session['resume_id'] = resume.id
            return redirect('result')
    else:
        form = ResumeForm()
    return render(request, 'analyzer/upload.html', {'form': form})


# Result View
def result(request):
    resume_id = request.session.get('resume_id')
    if not resume_id:
        return redirect('upload_resume')

    resume = Resume.objects.get(id=resume_id)

    # Only generate feedback if not already cached
    if 'feedback' not in request.session:
        file_path = resume.file.path
        resume_text = "Unsupported file type."
        if file_path.endswith('.docx'):
            import docx2txt
            resume_text = docx2txt.process(file_path)
        elif file_path.endswith('.pdf'):
            import PyPDF2
            reader = PyPDF2.PdfReader(file_path)
            resume_text = "\n".join([page.extract_text() for page in reader.pages])

        feedback = get_ai_feedback(resume_text)
        request.session['feedback'] = feedback
    else:
        feedback = request.session['feedback']

    return render(request, 'analyzer/result.html', {'resume': resume, 'feedback': feedback})

# PDF Download View
def download_pdf(request):
    resume_id = request.session.get('resume_id')
    resume = Resume.objects.get(id=resume_id)
    feedback = request.session.get('feedback', 'No feedback available.')

    template_path = 'analyzer/pdf_template.html'
    context = {'resume': resume, 'feedback': feedback}

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.name}_AI_Feedback.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had an error generating the PDF.')
    return response
